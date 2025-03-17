from sqlalchemy.orm import Session
from app.models.profile import Profile

def get_profile(db: Session):
    return db.query(Profile).filter(Profile.id == "main_profile").first()

def update_profile(db: Session, profile_data: dict):
    profile = db.query(Profile).filter(Profile.id == "main_profile").first()
    if not profile:
        return None
        
    for key, value in profile_data.items():
        if value is not None:
            setattr(profile, key, value)
            
    db.commit()
    db.refresh(profile)
    return profile