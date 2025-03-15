from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class DesignSystem(Base):
    __tablename__ = "design_systems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    config = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<DesignSystem {self.name}>"