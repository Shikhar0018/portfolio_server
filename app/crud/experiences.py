from sqlalchemy.orm import Session
from app.models.experiences import ExperienceModel
from app.schemas.experiences import ExperienceCreate, ExperienceUpdate

def get_experiences(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ExperienceModel).offset(skip).limit(limit).all()

def get_experience(db: Session, experience_id: str):
    return db.query(ExperienceModel).filter(ExperienceModel.id == experience_id).first()

def create_experience(db: Session, experience: ExperienceCreate):
    db_experience = ExperienceModel(**experience.dict())
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)
    return db_experience

def update_experience(db: Session, experience_id: str, experience: ExperienceUpdate):
    db_experience = get_experience(db, experience_id=experience_id)
    if not db_experience:
        return None
    update_data = experience.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_experience, key, value)
    db.commit()
    db.refresh(db_experience)
    return db_experience

def delete_experience(db: Session, experience_id: str):
    db_experience = get_experience(db, experience_id=experience_id)
    if not db_experience:
        return False
    db.delete(db_experience)
    db.commit()
    return True
