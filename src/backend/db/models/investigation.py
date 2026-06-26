from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from src.backend.db.base import Base

class AgentFinding(Base):
    __tablename__ = "agent_findings"

    id = Column(String, primary_key=True)
    inspection_id = Column(String, ForeignKey("inspections.id"), nullable=False)
    probable_causes = Column(JSON, nullable=True)
    regulation_refs = Column(JSON, nullable=True)
    airworthiness_status = Column(String, nullable=True)
    recommended_action = Column(String, nullable=True)
    repair_steps = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())