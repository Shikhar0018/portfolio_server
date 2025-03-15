from sqlalchemy.orm import Session
from app.models.projects import ProjectModel
from app.schemas.projects import ProjectCreate, ProjectUpdate

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ProjectModel).offset(skip).limit(limit).all()

def get_project(db: Session, project_id: str):
    return db.query(ProjectModel).filter(ProjectModel.id == project_id).first()

def create_project(db: Session, project: ProjectCreate):
    db_project = ProjectModel(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: str, project: ProjectUpdate):
    db_project = get_project(db, project_id=project_id)
    if not db_project:
        return None
    update_data = project.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: str):
    db_project = get_project(db, project_id=project_id)
    if not db_project:
        return False
    db.delete(db_project)
    db.commit()
    return True
