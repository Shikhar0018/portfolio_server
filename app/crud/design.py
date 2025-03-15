from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.design import DesignSystem
from app.schemas.design import DesignSystemCreate, DesignSystemUpdate

def get_design_system(db: Session, design_id: int) -> Optional[DesignSystem]:
    return db.query(DesignSystem).filter(DesignSystem.id == design_id).first()

def get_design_system_by_name(db: Session, name: str) -> Optional[DesignSystem]:
    return db.query(DesignSystem).filter(DesignSystem.name == name).first()

def get_active_design_system(db: Session) -> Optional[DesignSystem]:
    return db.query(DesignSystem).filter(DesignSystem.is_active == True).first()

def get_design_systems(db: Session, skip: int = 0, limit: int = 100) -> List[DesignSystem]:
    return db.query(DesignSystem).offset(skip).limit(limit).all()

def create_design_system(db: Session, design_system: DesignSystemCreate) -> DesignSystem:
    db_design_system = DesignSystem(
        name=design_system.name,
        config=design_system.dict(exclude={"name"})
    )
    db.add(db_design_system)
    db.commit()
    db.refresh(db_design_system)
    return db_design_system

def update_design_system(
    db: Session, design_id: int, design_system: DesignSystemUpdate
) -> Optional[DesignSystem]:
    db_design_system = get_design_system(db, design_id)
    if not db_design_system:
        return None
    
    update_data = design_system.dict(exclude_unset=True)
    
    # Handle nested updates for config
    if any(key in update_data for key in ["colors", "dark_mode", "typography", "spacing", "border_radius"]):
        config = db_design_system.config.copy()
        for key in ["colors", "dark_mode", "typography", "spacing", "border_radius"]:
            if key in update_data:
                config[key] = update_data.pop(key)
        
        db_design_system.config = config
    
    # Update name if provided
    if "name" in update_data:
        db_design_system.name = update_data["name"]
    
    db.commit()
    db.refresh(db_design_system)
    return db_design_system

def set_active_design_system(db: Session, design_id: int) -> Optional[DesignSystem]:
    # First, deactivate all design systems
    db.query(DesignSystem).update({"is_active": False})
    
    # Then activate the specified one
    db_design_system = get_design_system(db, design_id)
    if not db_design_system:
        return None
    
    db_design_system.is_active = True
    db.commit()
    db.refresh(db_design_system)
    return db_design_system

def delete_design_system(db: Session, design_id: int) -> bool:
    db_design_system = get_design_system(db, design_id)
    if not db_design_system:
        return False
    
    # Don't allow deleting the active design system
    if db_design_system.is_active:
        return False
    
    db.delete(db_design_system)
    db.commit()
    return True