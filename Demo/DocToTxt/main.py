from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from database import BidNotice, get_db, init_db
from doc_converter import DocOleFileConverter

app = FastAPI(
    title="DOC to Txt Converter",
    description="DOC to Txt Converter",
    version="demo",
)

# Init
doc_converter = DocOleFileConverter()
init_db()

# upload doc
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

# convert doc olefile
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

    # DOC to TXT
    filename = f"{document.id}.doc"
    text, success = doc_converter.doc_to_txt_ole(document.ntceSpecFileNm, filename)
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