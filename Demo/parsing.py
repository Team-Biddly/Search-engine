import os
from typing import List, Optional
from fastapi import FastAPI, Depends, Query
from sqlalchemy import create_engine, Column, Integer, String, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'data.sqlite')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TextData(Base):
    __tablename__ = "TextData"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False) # 공고명
    file1 = Column(String(30), nullable=True)
    file2 = Column(String(30), nullable=True)
    file3 = Column(String(30), nullable=True)
    text1 = Column(String(500), nullable=False) # 본문
    text2 = Column(String(500), nullable=False)
    text3 = Column(String(500), nullable=False)

# --- Pydantic 스키마 ---
# 데이터 생성을 위한 스키마 (Postman에서 보낼 데이터 형식)
class TextDataCreate(BaseModel):
    name: str
    file1: Optional[str] = None
    file2: Optional[str] = None
    file3: Optional[str] = None
    text1: str
    text2: str = ""
    text3: str = ""

# 검색 결과를 위한 스키마
class SearchResultSchema(BaseModel):
    id: int
    name: Optional[str] = None
    matched_locations: List[str]  # [수정됨] location -> locations (변수명 일치)

    class Config:
        from_attributes = True

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def find_keyword_locations(item: TextData, keyword: str) -> List[str]:
    locations = []
    if item.name and keyword in item.name:
        locations.append(f"공고명({item.name})")
    if item.text1 and keyword in item.text1:
        locations.append(f"본문1(파일: {item.file1})")
    if item.file2 and keyword in item.file2:
        locations.append(f"파일명2({item.file2})")
    if item.text2 and keyword in item.text2:
        locations.append(f"본문2(파일: {item.file2})")
    return locations

# --- [API] 데이터 추가 (테스트용) ---
@app.post("/create")
def create_data(item: TextDataCreate, db: Session = Depends(get_db)):
    new_data = TextData(
        name=item.name,
        file1=item.file1, file2=item.file2, file3=item.file3,
        text1=item.text1, text2=item.text2, text3=item.text3
    )
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return {"message": "데이터가 성공적으로 저장되었습니다.", "id": new_data.id}

# --- [API] 검색 ---
@app.get("/search", response_model=List[SearchResultSchema])
def search_in_db(
        keyword: str = Query(..., min_length=1, description="검색할 단어"),
        db: Session = Depends(get_db)
):
    results = db.query(TextData).filter(
        or_(
            TextData.name.contains(keyword),
            TextData.file1.contains(keyword),
            TextData.file2.contains(keyword),
            TextData.file3.contains(keyword),
            TextData.text1.contains(keyword),
            TextData.text2.contains(keyword),
            TextData.text3.contains(keyword)
        )
    ).all()

    response_data = []
    for item in results:
        locs = find_keyword_locations(item, keyword)
        response_data.append(SearchResultSchema(
            id=item.id,
            name=item.name,
            matched_locations=locs # [수정됨] 스키마 변수명과 일치시킴
        ))
    return response_data