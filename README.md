```
Biddly_engine/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI 애플리케이션 진입점
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── upload.py        # 파일 업로드 엔드포인트
│   │   │   │   ├── search.py        # 검색 엔드포인트
│   │   │   │   └── status.py        # 처리 상태 조회
│   │   │   └── router.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # 환경설정 (한컴 API 키 등)
│   │   ├── constants.py             # 상수 정의 (지원 확장자 등)
│   │   └── exceptions.py            # 커스텀 예외
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── classifier/
│   │   │   ├── __init__.py
│   │   │   ├── primary.py           # 1차 분류 (확장자)
│   │   │   └── secondary.py         # 2차 분류 (헤더/라이브러리)
│   │   │
│   │   ├── converter/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # 변환기 인터페이스
│   │   │   ├── pdf_converter.py    # PDF → TXT
│   │   │   └── office_converter.py # HWP/DOC/PPT/XLS → TXT (한컴 API)
│   │   │
│   │   ├── queue/
│   │   │   ├── __init__.py
│   │   │   ├── buffer_manager.py   # 버퍼/큐 관리
│   │   │   └── redis_queue.py      # Redis 큐 (선택적)
│   │   │
│   │   └── parser/
│   │       ├── __init__.py
│   │       ├── text_parser.py      # 텍스트 파싱
│   │       └── search_engine.py    # 검색 엔진
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py              # 문서 모델
│   │   └── search.py                # 검색 요청/응답 모델
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── document.py              # Pydantic 스키마
│   │   └── search.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── file_validator.py        # 파일 검증
│       ├── header_detector.py       # 파일 헤더 감지
│       └── logger.py                # 로깅 유틸
│
├── tests/
│   ├── __init__.py
│   ├── test_classifier.py
│   ├── test_converter.py
│   └── test_api.py
│
├── data/
│   ├── uploads/                     # 임시 업로드 파일
│   ├── processed/                   # 처리된 텍스트 파일
│   └── queue/                       # 큐 데이터 (파일 기반 시)
│
├── logs/
│   └── app.log
│
├── requirements.txt
├── .env                             # 환경변수
├── .gitignore
└── README.md
```