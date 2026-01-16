import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)#객체 생성
basedir=os.path.abspath(os.path.dirname(__file__))
#__file__: 현재 이 파이썬 파일의 전체 경로 예) C:\project\app.py

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite') #db의 주소 연결?
#app.config[]:flask 앱의 설정을 저장하는 딕셔너리
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class TextData(db.Model):
    id=db.Column(db.Integer,primary_key=True) #primary_key-> id자동으로 부여
    name=db.Column(db.String(30),nullable=True)  #공고명

    file1 = db.Column(db.String(30), nullable=True)  # 파일명
    file2 = db.Column(db.String(30), nullable=True)
    file3 = db.Column(db.String(30), nullable=True)

    text1=db.Column(db.String(500),nullable=False) #본문(텍스트)
    text2=db.Column(db.String(500),nullable=False)
    text3=db.Column(db.String(500),nullable=False)


    def __repr__(self):
        return f"<TextData={self.content}>"
def setup_database():
    with app.app_context():
        db.create_all()


def search_in_db(keyword):
    with app.app_context():
        # 모든 컬럼에서 키워드 검색
        result = TextData.query.filter(
            (TextData.name.contains(keyword)) |      # name 검색
            (TextData.file1.contains(keyword)) |     # file1 검색
            (TextData.file2.contains(keyword)) |     # file2 검색
            (TextData.file3.contains(keyword)) |     # file3 검색
            (TextData.text1.contains(keyword)) |     # text1 검색
            (TextData.text2.contains(keyword)) |     # text2 검색
            (TextData.text3.contains(keyword))       # text3 검색
        ).all()
        return result


def find_keyword_locations(item, keyword):

    locations = []

    # name에 키워드가 있는지
    if item.name and keyword in item.name:
        locations.append(f"공고명({item.name})")

    # file1, text1에 키워드가 있는지
    if item.file1 and keyword in item.file1:
        locations.append(f"파일명1({item.file1})")
    if item.text1 and keyword in item.text1:
        locations.append(f"본문1(파일: {item.file1})")

    # file2, text2에 키워드가 있는지
    if item.file2 and keyword in item.file2:
        locations.append(f"파일명2({item.file2})")
    if item.text2 and keyword in item.text2:
        locations.append(f"본문2(파일: {item.file2})")

    # file3, text3에 키워드가 있는지
    if item.file3 and keyword in item.file3:
        locations.append(f"파일명3({item.file3})")
    if item.text3 and keyword in item.text3:
        locations.append(f"본문3(파일: {item.file3})")

    return locations
#메인 실행부
if __name__=="__main__":
    setup_database() #이전에 선언했던 함수.테이블 만들고 테이블의 content들이 비어있다면 내용 추가.
    search_term=input("\n찾고싶은 단어를 검색해주세요.")
    print(f"\n{search_term}을(를) 포함하는 문장 찾는 중...\n")
    matched_results=search_in_db(search_term) #검색 단어가 테이블에 있는지/없는지

    if matched_results:
        print(f"검색 결과 ({len(matched_results)}개):\n")
        for idx, item in enumerate(matched_results, 1):
            # 어디에 키워드가 있는지 찾기
            locations = find_keyword_locations(item, search_term)

            # 결과 출력
            print(f"--- 결과 {idx} ---")
            print(f"ID: {item.id}")
            print(f"공고명: {item.name}")
            print(f"키워드 발견 위치:")
            for loc in locations:
                print(f"  ✓ {loc}")
    else:
        print("해당 단어를 찾을 수 없습니다!")

