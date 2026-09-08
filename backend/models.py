from sqlalchemy import Column, Integer, String
from .database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String, unique=True, index=True)
    product_id = Column(String, index=True)
    product_name = Column(String)
    category = Column(String)
    overall_status = Column(String)
    violation_type = Column(String)
    fields_json = Column(String)
    raw_ocr_json = Column(String)
