from typing import Optional, Union
from pydantic import BaseModel, EmailStr
from datetime import datetime
# from __future__ import annotations

class ProfileBase(BaseModel):
    name: str
    description: str
    email: EmailStr
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    professional_background: Optional[str] = None
    journey: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    email: Optional[EmailStr] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    professional_background: Optional[str] = None
    journey: Optional[str] = None