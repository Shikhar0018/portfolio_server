from sqlalchemy import Column, String, ARRAY, Text
from app.core.database import Base

class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    image = Column(String, nullable=False)
    technologies = Column(ARRAY(String), nullable=False)
    link = Column(String, nullable=False)
    github = Column(String, nullable=True)
    appStore = Column(String, nullable=True)
    playStore = Column(String, nullable=True)
    achievements = Column(ARRAY(String), nullable=False)
