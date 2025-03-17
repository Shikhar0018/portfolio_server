from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.api.deps import get_db
from app.crud import experiences as experiences_crud
from app.crud import projects as projects_crud

router = APIRouter()

@router.get("/portfolio", response_model=Dict[str, Any])
def get_portfolio_data(
    db: Session = Depends(get_db)
):
    """
    Get complete portfolio data including:
    - All experiences
    - All projects
    """
    try:
        # Get all experiences
        experiences = experiences_crud.get_experiences(db)
        
        # Get all projects
        projects = projects_crud.get_projects(db)
        
        return {
            "experiences": experiences,
            "projects": projects
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching portfolio data: {str(e)}"
        )