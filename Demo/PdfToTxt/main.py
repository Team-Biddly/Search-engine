from pdf_converter import PdfFileConverter
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from database import BidNotice, get_db, init_db

app = FastAPI(
    title="PDF to Txt Converter",
    description="PDF to Txt Converter",
    version="demo",
)

pdf_converter = PdfFileConverter()
init_db()

@app.post("/test/pdf_convert/{notice_id}", tags=["test"])
async def test_pdf_convert(
        notice_id: int,
        db: Session = Depends(get_db),
):
    """
    Method: Post
    Description: DB에 저장된 PDF 바이너리를 읽어 텍스트로 변환 후 DB 업데이트
    """
    # 1. DB에서 파일 정보 조회
    document = db.query(BidNotice).filter(BidNotice.id == notice_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Notice not found")
    if not document.ntceSpecFileNm:
        raise HTTPException(status_code=404, detail="File binary not found")

    # 2. 파일 확장자 검증 (선택사항이지만 안전을 위해 권장)
    if not document.ntceSpecFile.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="This file is not a PDF")

    # 3. PDF to TXT 변환
    # DB의 LargeBinary(document.ntceSpecFileNm)를 그대로 넘깁니다.
    text, success = pdf_converter.pdf_to_txt(document.ntceSpecFileNm)

    print(f"[PDF Overview] {text[:100]}...")  # 로그 확인용

    # 4. 결과 저장
    if success:
        document.converted_txt = text
        document.is_converted = True
    else:
        # 실패 시 에러 메시지를 저장하거나 플래그만 False로 설정
        document.is_converted = False
        print(f"Conversion Failed: {text}")  # 실패 시 text변수에 에러메시지가 담김

    db.commit()
    db.refresh(document)

    return {
        "status": "success" if success else "failed",
        "document_id": document.id,
        "is_converted": document.is_converted,
        "filename": document.ntceSpecFile
    }