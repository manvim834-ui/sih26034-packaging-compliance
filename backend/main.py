import os
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, SessionLocal
from . import models
import uuid
import shutil
import json
from sqlalchemy.orm import Session
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi import FastAPI, UploadFile, File, Form, Depends
from typing import List


Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/scan")
def scan(file: UploadFile = File(...), db: Session = Depends(get_db)):
    from ocr.ocr_pipeline import run_ocr_pipeline
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
def batch(
    product_id: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    from ocr.multi_image import aggregate_product_images

    temp_paths = []
    for f in files:
        temp_path = f"temp_{uuid.uuid4().hex}.jpg"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        temp_paths.append(temp_path)

    try:
        result = aggregate_product_images(product_id, temp_paths)
    finally:
        for path in temp_paths:
            os.remove(path)

    fields = {}
    for field, candidates in result["candidates_by_field"].items():
        best = candidates[0]
        fields[field] = {
            "value": best["text"],
            "confidence": best["confidence"],
            "status": best["status"],
            "source_image": best["source_image"]
        }

    batch_id = uuid.uuid4().hex[:8]

    db_scan = models.Scan(
        scan_id=batch_id,
        product_id=product_id,
        product_name="unknown",
        category="unknown",
        overall_status="pending_extraction",
        violation_type=None,
        fields_json=json.dumps(fields),
        raw_ocr_json=json.dumps(result["combined_lines"])
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)

    return {
        "batch_id": batch_id,
        "product_id": product_id,
        "images_processed": result["images_processed"],
        "fields": fields
    }
