from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session

from classification import process_file_by_type
from classification import FileClassifier
from database import BidNotice, get_db, init_db

from DocToTxt.doc_converter import DocConverter
from HwpToTxt.hwp_converter import HwpConverter
from PdfToTxt.pdf_converter import PdfConverter

app = FastAPI(
    title="File to Txt Converter",
    description="File to Txt Converter with Classifier",
    version="demo",
)

# Init
classifier = FileClassifier()
hwp_converter = HwpConverter()
doc_converter = DocConverter()
pdf_converter = PdfConverter()

init_db()

# file classifier
@app.post("/test/classify", tags=["test"])
async def test_classify(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """
    Method: Post
    Body: form-data
    Key: file
    """
    file_type = classifier.classify(file.filename)
    result = await process_file_by_type(file, file_type)

    print(f"{result}")

    content = await file.read()
    result_save = BidNotice(
        ntceSpecFile=file.filename,
        ntceSpecFileNm=content,
        converted_txt=result.get("text", ""),
        is_converted=result.get("success", False),
    )
    db.add(result_save)
    db.commit()
    db.refresh(result_save)

    return {
        "filename": file.filename,
        "file_type": file_type,
        "success": result.get("success", False),
        "converted_txt": result.get("text", ""),
        "message": result.get("message", ""),
    }

# upload file
@app.post("/test/upload", tags=["test"])
async def test_upload(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
):
    """
    Method: Post
    Body: form-data
    Key: file
    """
    try:
        content = await file.read()
        notice = BidNotice(
            ntceSpecFile=file.filename,
            ntceSpecFileNm=content,
        )
        db.add(notice)
        db.commit()
        db.refresh(notice)

        return {
            "status": "success",
            "message": "success",
            "notice_id": notice.id,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#================================= HWP =================================
# convert hwp olefile
@app.post("/test/hwp_convert/{notice_id}", tags=["test"])
async def test_ole_convert(
        notice_id: int,
        db: Session = Depends(get_db),
):
    """
    Method: Post
    """
    document = db.query(BidNotice).filter(BidNotice.id == notice_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Notice not found")
    if not document.ntceSpecFileNm:
        raise HTTPException(status_code=404, detail="NTC Spec file not found")

    # HWP to TXT
    filename = f"{document.id}.hwp"
    text, success = hwp_converter.hwp_to_txt(document.ntceSpecFileNm, filename)
    print(f"[overview] {text}")
    if success:
        document.converted_txt = text
        document.is_converted = True
    else:
        document.is_converted = False

    db.commit()
    db.refresh(document)

    return {
        "status": "success" if success else "failed",
        "document_id": document.id,
        "is_converted": document.is_converted,
    }


# Search For Keyword
@app.get("/test/search", tags=["test"])
async def test_search(
        keyword: str,
        db: Session = Depends(get_db),
):
    """
    Method: Get
    Query Parameter: keyword
    """
    try:
        documents = db.query(BidNotice).filter(
            BidNotice.converted_txt.isnot(None),
            BidNotice.converted_txt.contains(keyword),
            BidNotice.converted_txt.like(f"%{keyword}%"),
        ).all()

        matched_results = [
            {
                "id": doc.id,
                "file name": f"{doc.ntceSpecFile}",
                "file 미리보기": f"{doc.converted_txt[:100]}"
            }
            for doc in documents
        ]

        return {
            "status": "success",
            "keyword": keyword,
            "matched_count": len(matched_results),
            "matched_results": matched_results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#================================= DOC =================================
# convert doc file
@app.post("/test/doc_convert/{notice_id}", tags=["test"])
async def test_ole_convert(
        notice_id: int,
        db: Session = Depends(get_db),
):
    """
    Method: Post
    """
    document = db.query(BidNotice).filter(BidNotice.id == notice_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Notice not found")
    if not document.ntceSpecFileNm:
        raise HTTPException(status_code=404, detail="NTC Spec file not found")

    # HWP to TXT
    filename = f"{document.id}.hwp"
    text, success = doc_converter.doc_to_txt(document.ntceSpecFileNm, filename)
    print(f"[overview] {text}")
    if success:
        document.converted_txt = text
        document.is_converted = True
    else:
        document.is_converted = False

    db.commit()
    db.refresh(document)

    return {
        "status": "success" if success else "failed",
        "document_id": document.id,
        "is_converted": document.is_converted,
    }


# Search For Keyword
@app.get("/test/search", tags=["test"])
async def test_search(
        keyword: str,
        db: Session = Depends(get_db),
):
    """
    Method: Get
    Query Parameter: keyword
    """
    try:
        documents = db.query(BidNotice).filter(
            BidNotice.converted_txt.isnot(None),
            BidNotice.converted_txt.contains(keyword),
            BidNotice.converted_txt.like(f"%{keyword}%"),
        ).all()

        matched_results = [
            {
                "id": doc.id,
                "file name": f"{doc.ntceSpecFile}",
                "file 미리보기": f"{doc.converted_txt[:100]}"
            }
            for doc in documents
        ]

        return {
            "status": "success",
            "keyword": keyword,
            "matched_count": len(matched_results),
            "matched_results": matched_results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#================================= PDF =================================
#pdf로 변환하여 저장
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