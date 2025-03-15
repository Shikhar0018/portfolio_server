from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import design as design_crud
from app.schemas.design import (
    DesignSystemCreate,
    DesignSystemUpdate,
    DesignSystemResponse,
    ColorScheme
)

router = APIRouter()

@router.get("/color-scheme", response_model=ColorScheme)
def get_color_scheme(
    db: Session = Depends(get_db)
):
    """
    Get the current color scheme from the active design system
    """
    design_system = design_crud.get_active_design_system(db)
    if not design_system:
        # Return default color scheme if no active design system
        from app.core.config import settings
        return settings.DEFAULT_DESIGN_SYSTEM["colors"]
    
    return design_system.config["colors"]

@router.put("/color-scheme", response_model=ColorScheme)
def update_color_scheme(
    color_scheme: ColorScheme,
    db: Session = Depends(get_db)
):
    """
    Update the color scheme of the active design system
    """
    design_system = design_crud.get_active_design_system(db)
    if not design_system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active design system found"
        )
    
    # Update only the colors part of the design system
    config = design_system.config.copy()
    config["colors"] = color_scheme.dict()
    
    # Create update object with only the config field
    update_data = DesignSystemUpdate(config=config)
    
    updated = design_crud.update_design_system(
        db, design_id=design_system.id, design_system=update_data
    )
    
    return updated.config["colors"]

@router.post("/", response_model=DesignSystemResponse, status_code=status.HTTP_201_CREATED)
def create_design_system(
    design_system: DesignSystemCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new design system
    """
    db_design_system = design_crud.get_design_system_by_name(db, name=design_system.name)
    if db_design_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Design system with this name already exists"
        )
    return design_crud.create_design_system(db=db, design_system=design_system)

@router.get("/", response_model=List[DesignSystemResponse])
def read_design_systems(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all design systems
    """
    design_systems = design_crud.get_design_systems(db, skip=skip, limit=limit)
    return design_systems

@router.get("/active", response_model=DesignSystemResponse)
def read_active_design_system(
    db: Session = Depends(get_db)
):
    """
    Get the currently active design system
    """
    design_system = design_crud.get_active_design_system(db)
    if not design_system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active design system found"
        )
    return design_system

@router.get("/{design_id}", response_model=DesignSystemResponse)
def read_design_system(
    design_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific design system by ID
    """
    design_system = design_crud.get_design_system(db, design_id=design_id)
    if not design_system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Design system not found"
        )
    return design_system

@router.put("/{design_id}", response_model=DesignSystemResponse)
def update_design_system(
    design_id: int,
    design_system: DesignSystemUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a design system
    """
    db_design_system = design_crud.update_design_system(
        db, design_id=design_id, design_system=design_system
    )
    if not db_design_system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Design system not found"
        )
    return db_design_system

@router.post("/{design_id}/activate", response_model=DesignSystemResponse)
def activate_design_system(
    design_id: int,
    db: Session = Depends(get_db)
):
    """
    Set a design system as active
    """
    db_design_system = design_crud.set_active_design_system(db, design_id=design_id)
    if not db_design_system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Design system not found"
        )
    return db_design_system

@router.delete("/{design_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_design_system(
    design_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a design system
    """
    success = design_crud.delete_design_system(db, design_id=design_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete design system (it might be active or not found)"
        )
    return None