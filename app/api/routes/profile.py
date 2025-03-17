from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.crud.profile import get_profile, update_profile

router = APIRouter()

@router.get("/profile", response_model=ProfileResponse)
def read_profile(db: Session = Depends(get_db)):
    profile = get_profile(db)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

@router.put("/profile", response_model=ProfileResponse)
def update_profile_endpoint(
    update_data: ProfileUpdate,
    db: Session = Depends(get_db)
):
    profile = update_profile(db, update_data.dict(exclude_unset=True))
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile