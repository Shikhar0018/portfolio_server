from sqlalchemy import Column, String, ARRAY, Text
from app.core.database import Base

class ExperienceModel(Base):
    __tablename__ = "experiences"

    id = Column(String, primary_key=True)
    role = Column(String, nullable=False)
    company = Column(String, nullable=False)
    period = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    achievements = Column(ARRAY(String), nullable=False)
    projects = Column(ARRAY(String), nullable=False)
    color = Column(String, nullable=False)
