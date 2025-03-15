from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import experiences as experiences_crud
from app.schemas.experiences import (
    Experience,
    ExperienceCreate,
    ExperienceUpdate
)

router = APIRouter()

@router.get("/", response_model=List[Experience])

def get_experiences(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all work experiences
    """
    return experiences_crud.get_experiences(db, skip=skip, limit=limit)

@router.get("/{experience_id}", response_model=Experience)
def get_experience(
    experience_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific experience by ID
    """
    experience = experiences_crud.get_experience(db, experience_id=experience_id)
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    return experience

@router.post("/", response_model=Experience, status_code=status.HTTP_201_CREATED)
def create_experience(
    experience: ExperienceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new work experience
    """
    return experiences_crud.create_experience(db, experience=experience)

@router.put("/{experience_id}", response_model=Experience)
def update_experience(
    experience_id: str,
    experience: ExperienceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a work experience
    """
    db_experience = experiences_crud.update_experience(
        db, experience_id=experience_id, experience=experience
    )
    if not db_experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    return db_experience

@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(
    experience_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a work experience
    """
    success = experiences_crud.delete_experience(db, experience_id=experience_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    return None
