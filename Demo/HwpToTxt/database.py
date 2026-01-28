from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# DB Setting (Sqlite For Test)
SQLALCHEMY_DATABASE_URI = "sqlite:///HwpToTxt_Test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BidNotice(Base):
    """나라 장터 입찰 공고"""
    __tablename__ = "bid_notice"

    id = Column(Integer, primary_key=True, index=True)
    ntceSpecFileNm = Column(String, index=True) # HWP File name
    ntceSpecFile = Column(LargeBinary, index=True) # HWP File
    converted_txt = Column(Text, nullable=True)
    is_converted = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

def init_db():
    Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()