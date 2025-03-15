
from typing import List, Optional
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    title: str
    description: str
    image: str
    technologies: List[str]
    link: str
    github: Optional[str] = None
    appStore: Optional[str] = None
    playStore: Optional[str] = None
    achievements: List[str]

class ProjectCreate(ProjectBase):
    id: str

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    technologies: Optional[List[str]] = None
    link: Optional[str] = None
    github: Optional[str] = None
    appStore: Optional[str] = None
    playStore: Optional[str] = None
    achievements: Optional[List[str]] = None

class Project(ProjectBase):
    id: str

    class Config:
        orm_mode = True
