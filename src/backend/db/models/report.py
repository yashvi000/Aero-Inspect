from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.backend.db.base import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True)
    inspection_id = Column(String, ForeignKey("inspections.id"), nullable=False)
    defect_report_path = Column(String, nullable=True)
    work_order_path = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())