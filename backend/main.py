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
    from rules.classifier import classify_package
    from rules.rule_engine import run_rule_engine

    temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        ocr_result = run_ocr_pipeline(temp_filename, keep_all_variants=False)
    finally:
        os.remove(temp_filename)

    package_type = classify_package(ocr_result["lines"])
    compliance_result = run_rule_engine(
        ocr_result["lines"], package_type=package_type)

    fields = compliance_result["fields"]
    overall_status = compliance_result["overall_verdict"]
    failed_fields = [f for f, r in fields.items() if r["status"] == "FAIL"]
    violation_type = ", ".join(failed_fields) if failed_fields else None

    scan_id = uuid.uuid4().hex[:8]

    db_scan = models.Scan(
        scan_id=scan_id,
        product_id="unknown",
        product_name="unknown",
        category="unknown",
        overall_status=overall_status,
        violation_type=violation_type,
        fields_json=json.dumps(fields),
        raw_ocr_json=json.dumps(ocr_result)
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)

    return {
        "scan_id": scan_id,
        "package_type": package_type,
        "overall_status": overall_status,
        "violation_type": violation_type,
        "fields": fields
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
    from rules.classifier import classify_package
    from rules.rule_engine import run_rule_engine

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

    package_type = classify_package(result["combined_lines"])
    compliance_result = run_rule_engine(
        result["combined_lines"], package_type=package_type)

    fields = compliance_result["fields"]
    overall_status = compliance_result["overall_verdict"]
    failed_fields = [f for f, r in fields.items() if r["status"] == "FAIL"]
    violation_type = ", ".join(failed_fields) if failed_fields else None

    batch_id = uuid.uuid4().hex[:8]

    db_scan = models.Scan(
        scan_id=batch_id,
        product_id=product_id,
        product_name="unknown",
        category="unknown",
        overall_status=overall_status,
        violation_type=violation_type,
        fields_json=json.dumps(fields),
        raw_ocr_json=json.dumps(result["combined_lines"])
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)

    return {
        "batch_id": batch_id,
        "product_id": product_id,
        "package_type": package_type,
        "images_processed": result["images_processed"],
        "overall_status": overall_status,
        "violation_type": violation_type,
        "fields": fields
    }
