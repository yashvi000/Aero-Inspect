from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from src.backend.db.base import Base

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(String, primary_key=True)
    aircraft_type = Column(String, nullable=False)
    zone_id = Column(String, nullable=True)
    inspection_type = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String, default="CREATED")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())