from typing import List, Optional
from pydantic import BaseModel

class ExperienceBase(BaseModel):
    role: str
    company: str
    period: str
    description: str
    achievements: List[str]
    projects: List[str]
    color: str

class ExperienceCreate(ExperienceBase):
    id: str

class ExperienceUpdate(BaseModel):
    role: Optional[str] = None
    company: Optional[str] = None
    period: Optional[str] = None
    description: Optional[str] = None
    achievements: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    color: Optional[str] = None

class Experience(ExperienceBase):
    id: str

    class Config:
        orm_mode = True
