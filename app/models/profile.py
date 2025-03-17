from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(String, primary_key=True, index=True, default="main_profile")
    name = Column(String(100), nullable=False)
    description = Column(Text)
    email = Column(String(100), nullable=False)
    linkedin_url = Column(String(200))
    github_url = Column(String(200))
    professional_background = Column(Text)
    journey = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())