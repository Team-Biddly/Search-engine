### [26.1.20]  SQLAlchemy의 Engine과 Session ###

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
