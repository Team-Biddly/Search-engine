from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from database import BidNotice, get_db, init_db
from hwp_converter import HWPConverter

app = FastAPI(
    title="HWP to Txt Converter",
    description="HWP to Txt Converter",
    version="demo",
)

# Init
converter = HWPConverter(api_key="~~~~")
init_db()

# upload hwp api
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

# convert hwp api
@app.post("/test/convert/{notice_id}", tags=["test"])
async def test_convert(
        notice_id: int,
        db: Session = Depends(get_db),
):
    """
    Method: Post
    URL: http://127.0.0.1:5000/test/convert/{notice_id}
    """
    document = db.query(BidNotice).filter(BidNotice.id == notice_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Notice not found")
    if not document.ntceSpecFile:
        raise HTTPException(status_code=404, detail="NTC Spec file not found")

    # HWP to TXT
    filename = f"{document.id}.hwp"
    success, text = converter.hwp_to_txt(document.ntceSpecFile, filename)
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
        "notice_id": document.notice_id,
        "is_converted": document.is_converted,
    }