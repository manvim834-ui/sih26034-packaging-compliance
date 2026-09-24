import os
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, SessionLocal
from . import models
import uuid
import shutil
import json
from sqlalchemy.orm import Session
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
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
    from rules.ingredient_checker import check_banned_ingredients
    from rules.tampering_detector import detect_mrp_tampering

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail="Uploaded file must be an image (jpg, png, etc.)")

    temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        try:
            ocr_result = run_ocr_pipeline(
                temp_filename, keep_all_variants=False)
        except Exception as e:
            raise HTTPException(
                status_code=422, detail=f"Could not process image: {str(e)}")

        if ocr_result["status"] == "no_text_detected":
            return {
                "scan_id": None,
                "overall_status": "no_text_detected",
                "message": "No readable text was found on this image. Try a clearer, well-lit photo.",
                "fields": {}
            }

        package_type = classify_package(ocr_result["lines"])
        compliance_result = run_rule_engine(
            ocr_result["lines"], package_type=package_type)
        fields = compliance_result["fields"]

        ocr_text = "\n".join(
            line.get("text", "") for line in ocr_result["lines"] if line.get("text")
        )
        ingredient_result = check_banned_ingredients(ocr_text)

        mrp_bbox = None
        for line in ocr_result["lines"]:
            if line.get("candidate_field") == "mrp" or "mrp" in (line.get("candidate_fields") or []):
                mrp_bbox = line.get("bbox")
                break

        tampering_result = detect_mrp_tampering(temp_filename, mrp_bbox)

        fields["banned_ingredient_check"] = ingredient_result
        fields["mrp_tampering_check"] = tampering_result

    finally:
        os.remove(temp_filename)

    overall_status = compliance_result["overall_verdict"]
    failed_fields = [f for f, r in fields.items() if isinstance(
        r, dict) and r.get("status") == "FAIL"]
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
    scans = db.query(models.Scan).order_by(
        models.Scan.created_at.desc()
    ).all()

    result = []

    for s in scans:
        result.append({
            "scan_id": s.scan_id,
            "product_id": s.product_id,
            "product_name": s.product_name,
            "category": s.category,
            "overall_status": s.overall_status,
            "violation_type": s.violation_type,
            "timestamp": (
                s.created_at.isoformat()
                if s.created_at
                else None
            ),
            "fields": json.loads(s.fields_json)
        })

    return result


@app.get("/scans/{scan_id}")
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(models.Scan).filter(models.Scan.scan_id == scan_id).first()

    if not scan:
        raise HTTPException(
            status_code=404, detail=f"No scan found with scan_id '{scan_id}'")

    raw_ocr = json.loads(scan.raw_ocr_json) if scan.raw_ocr_json else None
    raw_lines = raw_ocr.get("lines", raw_ocr) if isinstance(
        raw_ocr, dict) else raw_ocr

    return {
        "scan_id": scan.scan_id,
        "product_id": scan.product_id,
        "product_name": scan.product_name,
        "category": scan.category,
        "overall_status": scan.overall_status,
        "violation_type": scan.violation_type,
        "fields": json.loads(scan.fields_json),
        "raw_ocr_lines": [line.get("text") for line in raw_lines] if raw_lines else [],
        "timestamp": (
            scan.created_at.isoformat()
            if scan.created_at
            else None
        ),
        "raw_ocr": raw_ocr
    }


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
    failed_fields = [
        f for f, r in fields.items() if r["status"] == "FAIL"]
    violation_type = ", ".join(
        failed_fields) if failed_fields else None

    batch_id = uuid.uuid4().hex[:8]

    db_scan = models.Scan(
        scan_id=batch_id,
        product_id=product_id,
        product_name="unknown",
        category=package_type,
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
