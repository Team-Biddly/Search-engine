from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from database import BidNotice, get_db, init_db
from hwp_converter import HwpConverter

app = FastAPI(
    title="HWP to Txt Converter",
    description="HWP to Txt Converter",
    version="demo",
)

# Init
ole_converter = HwpConverter()
init_db()

# upload hwp
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
            ntceSpecFileNm=file.filename,
            ntceSpecFileN=content,
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

# convert hwp olefile
@app.post("/test/hwp_convert/{notice_id}", tags=["test"])
async def test_hwp_convert(
        notice_id: int,
        db: Session = Depends(get_db),
):
    """
    Method: Post
    """
    document = db.query(BidNotice).filter(BidNotice.id == notice_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Notice not found")
    if not document.ntceSpecFile:
        raise HTTPException(status_code=404, detail="NTC Spec file not found")

    # HWP to TXT
    filename = f"{document.id}.hwp"
    text, success = ole_converter.hwp_to_txt(document.ntceSpecFile, filename)
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
                "file name": f"{doc.ntceSpecFileNm}",
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