from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from database import BidNotice, get_db, init_db
from hwp_api_converter import HwpApiConverter
from hwp_olefile_converter import HwpOleFileConverter

app = FastAPI(
    title="HWP to Txt Converter",
    description="HWP to Txt Converter",
    version="demo",
)

# Init
api_converter = HwpApiConverter(api_key="~~~~")
ole_converter = HwpOleFileConverter()
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
@app.post("/test/api_convert/{notice_id}", tags=["test"])
async def test_api_convert(
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
    success, text = api_converter.hwp_to_txt_api(document.ntceSpecFileNm, filename)
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

# convert hwp olefile
@app.post("/test/ole_convert/{notice_id}", tags=["test"])
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
    text, success = ole_converter.hwp_to_txt_ole(document.ntceSpecFileNm, filename)

    print(f"[overview] {repr(text[:100]) if text else None}")
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