from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
import json
import shutil
import uuid
import os

from database import Base, engine, SessionLocal
import models
from ocr_pipeline import run_ocr_pipeline

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/scan")
def scan(file: UploadFile = File(...), db: Session = Depends(get_db)):
    temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        ocr_result = run_ocr_pipeline(temp_filename, keep_all_variants=False)
    finally:
        os.remove(temp_filename)

    scan_id = uuid.uuid4().hex[:8]

    fake_fields = {
        "manufacturer_name": {"value": "not_extracted_yet", "status": "pending"},
        "net_quantity": {"value": "not_extracted_yet", "status": "pending"},
        "mfg_date": {"value": "not_extracted_yet", "status": "pending"},
        "mrp": {"value": "not_extracted_yet", "status": "pending"}
    }

    db_scan = models.Scan(
        scan_id=scan_id,
        product_id="unknown",
        product_name="unknown",
        category="unknown",
        overall_status="pending_extraction",
        violation_type=None,
        fields_json=json.dumps(fake_fields),
        raw_ocr_json=json.dumps(ocr_result)
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)

    return {
        "scan_id": scan_id,
        "ocr_status": ocr_result["status"],
        "overall_confidence": ocr_result["overall_confidence"],
        "lines_detected": len(ocr_result["lines"]),
        "fields": fake_fields
    }


@app.get("/history")
def history(db: Session = Depends(get_db)):
    scans = db.query(models.Scan).all()
    result = []
    for s in scans:
        result.append({
            "scan_id": s.scan_id,
            "product_id": s.product_id,
            "overall_status": s.overall_status,
            "fields": json.loads(s.fields_json)
        })
    return result


@app.post("/batch")
def batch():
    return {"message": "batch endpoint placeholder"}
