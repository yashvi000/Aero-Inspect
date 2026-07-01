from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.backend.db.base import Base

class DetectionFinding(Base):
    __tablename__ = "defect_findings"

    id = Column(String, primary_key=True)
    inspection_id = Column(String, ForeignKey("inspections.id"), nullable=False)
    defect_type = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    severity = Column(String, nullable=True)
    bbox_x = Column(Integer, nullable=True)
    bbox_y = Column(Integer, nullable=True)
    bbox_w = Column(Integer, nullable=True)
    bbox_h = Column(Integer, nullable=True)
    zone = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())