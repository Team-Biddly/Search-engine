### TIL [26.1.20] SQLAlchemy의 Engine과 Session ###

## 핵심개념 ##
```
Engine (연결 풀)
   ↓ bind
SessionLocal (세션 팩토리)
   ↓ 호출할 때마다 생성
Session (실제 일꾼)

```
**1. Engine-데이터베이스 연결 풀**
   ```
   engine = create_engine('sqlite:///mydb.db')
   ```
**특징**
1) 앱 전체에서 1개만 생성
2) db 서버와의 물리적 연결 관리
3) 연결 풀 유지
4) 직접 쿼리 실행 안함

**2. SessionLocal-세션 팩토리**
   ```
   SessionLocal=sessionmaker(bind=engine)
   ```
**특징**
1) 앱 전체에서 1개만 생성
2) Session 객체를 찍어내는 공장
3) Engine과 연결 정보 보관
4) 직접 쿼리 실행 안함

**3. Session-실제 작업자**
   ```
   db=SessionLocal()
   ```
**특징**
1) 요청마다 새로 생성(독립적)
2) 실제 db 작업 수행
3) 사용 후 반드시 닫아야함

실제 작업
```
db.query(User).all()   #조회
db.add(user)           #추가
db.commit()            #db에 반영
db.rollback()          #취소
db.close()             #종료
```
### TIL [26.1.21]  SQLAlchemy의 Engine과 Session ###
 ORM=Obeject Relational Mapping(객체-관계 매핑)
: 데이터베이스 테이블을 python 클래스처럼 다루게 해주는 기술.

## 1. Base
```
Base = declarative_base()
```
   1) 모든 모델(테이블)의 기본 클래스
   2) 일반 클래스지만, DeclarativeMeta 메타클래스로 만들어져서 특별한 기능을 가짐
   3) 이것을 상속받는 모든 클래스에 orm기능을 자동으로 부여함
   4) ```declarative_base()```를 통해 생성됨
      
## 2. MetaData
   1) db를 전체적으로 관리하는데 용이
   2)``` Base```를 상속받은 모든 테이블들을 일괄적으로 관리할 수 있음.
   3) ```Base```를 상속받은 테이블이 생성되면 자동으로 metadata클래스에 추가됨
      

### <DB를 한번에 관리할 수 있는 예시>
1) 새 프로젝트 시작 - 테이블 한번에 생성
   ```
   engine = create_engine('sqlite:///mydb.db')
   Base.metadata.create_all(engine) #한줄로 모든 테이블 자동 생성
   ```
2) 개발 중 DB초기화
   ```
   Base.metadata.drop_all(engine) #한줄로 모두 삭제
   Base.metadata.create_all(engine) #한줄로 모두 재생성
   ```
3) 테스트환경-여러 DB에 같은 구조 만들기
   -> 시나리오: 개발DB,테스트DB,실서버DB 3개에 같은 테이블 만들어야 함
   ```
   #테이블 정의는 이미 되어있음

   #개발 DB생성
   dev_engine = create_engine('sqlite:///dev.db')
   Base.metadata.create_all(dev_engine)

   #테스트 DB에 생성
   test_engine = create_engine('sqlite:///test.db')
   Base.metadata.create_all(test_engine)

   #실서버 DB에 생성
   prod_engine = create_engine('postgresql://user:pass@server/db')
   Base.metadata.create_all(prod_engine)
   ```

### TIL [26.1.29] pydantic의 개념 및 존재 이유 ###

## 1. pydantic의 개념 ##
pydantic은 python 타입 힌트를 기반으로 데이터를 자동 검증하고 변환하는 라이브러리임
단순히 타입을 체크하는 것을 넘어, 잘못된 데이터가 들어오면 명확한 에러 메세지를 제공하고,
필요시 자동으로 타입을 변환함.

## 2. 핵심 기능 ##
1) 자동 데이터 검증
   ```
   class UploadResponse(BaseModel):
      status: str
      message: str
      notice_id: int #이때 문자열이 들어오면 자동으로 에러 발생
   ```
2) 타입 자동 변환
   ```
   # "123"(문자열) -> 123(정수)로 자동 변환 시도
   # 변환 불가능하면 validationError 발생

3) 명확한 api 스키마 정의
```
class SearchResponse(BaseModel):
   status: str
   keyword: str
   matched_coun: int
   matchend_results: List[SearchResultItem]
```
4) FastAPI 자동 문서화 연동
- swagger UI 에 요청/응답 예시 자동 생성
- 프론트엔드 개발자가 API명세를 쉽게 이해
  
5) 필드 커스터마이징
```
class SearchResultItem(BaseModel):
   id: int
   file_name: str=Field(..., alias="file name") #JSON 키 이름 변경
   preview: str=Filed(..., alias="file 미리보기") # 한글 키 지원
```










