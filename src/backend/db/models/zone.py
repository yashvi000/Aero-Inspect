from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.backend.db.base import Base

class Zone(Base):
    __tablename__ = "zones"

    id = Column(String, primary_key=True)
    zone_name = Column(String, nullable=False)
    zone_label = Column(String, nullable=False)
    current_status = Column(String, default="NORMAL")
    color = Column(String, default="GREEN")
    last_inspection_id = Column(String, ForeignKey("inspections.id"), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())