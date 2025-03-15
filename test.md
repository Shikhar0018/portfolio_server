Below are two files you can use:

1. **backend.md** – This is the complete documentation for your backend with all endpoints (design system, projects, experiences, and dynamic data).

2. **collection.json** – This Postman collection lets you easily test the API endpoints.

---

### backend.md

```markdown
# Dynamic Backend with Integrated Design System

This document outlines a complete implementation of a Python-based backend that supports dynamic data updates, a configurable design system, and now additional endpoints for managing projects and experiences.

## Technology Stack

- **Framework**: FastAPI (for high performance, easy-to-use API with automatic documentation)
- **Database**: SQLAlchemy with PostgreSQL (for data persistence)
- **Authentication**: JWT (JSON Web Tokens)
- **Deployment**: Docker (for containerization)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point (updated with design, projects, experiences, data)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Application configuration
│   │   ├── security.py           # Authentication and authorization
│   │   └── database.py           # Database connection management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── data.py           # Dynamic data CRUD endpoints
│   │   │   ├── design.py         # Design system endpoints (includes new color-scheme endpoints)
│   │   │   ├── projects.py       # Projects endpoints
│   │   │   └── experiences.py    # Experiences endpoints
│   │   └── deps.py               # Dependency injection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── data.py               # Dynamic data models
│   │   ├── design.py             # Design system models
│   │   ├── projects.py           # Project models
│   │   └── experiences.py        # Experience models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── data.py               # Pydantic models for data
│   │   ├── design.py             # Pydantic models for design system
│   │   ├── projects.py           # Pydantic models for projects
│   │   └── experiences.py        # Pydantic models for experiences
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py               # Base CRUD operations
│   │   ├── data.py               # Dynamic data CRUD operations
│   │   ├── design.py             # Design system CRUD operations
│   │   ├── projects.py           # Projects CRUD operations
│   │   └── experiences.py        # Experiences CRUD operations
│   └── utils/
│       ├── __init__.py
│       └── color_utils.py        # Utilities for color manipulation
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Test configuration
│   ├── test_data.py              # Tests for data endpoints
│   ├── test_design.py            # Tests for design system endpoints
│   ├── test_projects.py          # Tests for projects endpoints
│   └── test_experiences.py       # Tests for experiences endpoints
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── requirements.txt              # Python dependencies
├── .env.example                  # Example environment variables
└── README.md                     # Project documentation
```

## Implementation Details

### 1. Core Configuration (app/core/config.py)

```python
from pydantic import BaseSettings
from typing import Optional, Dict, Any, List
import json
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Design System API"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DATABASE_URL: str
    
    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Default design system
    DEFAULT_DESIGN_SYSTEM: Dict[str, Any] = {
        "colors": {
            "primary": "#8B5CF6",  # Purple
            "secondary": "#D946EF",  # Magenta
            "accent": "#F97316",  # Orange
            "background": "#FFFFFF",  # White
            "text": "#222222",  # Dark Gray
            "error": "#EA384C",  # Red
            "success": "#10B981",  # Green
            "warning": "#F59E0B",  # Amber
            "info": "#0EA5E9",  # Sky Blue
        },
        "dark_mode": {
            "background": "#1A1F2C",  # Dark Purple
            "text": "#FFFFFF",  # White
            "primary": "#9B87F5",  # Light Purple
        },
        "typography": {
            "font_family": "Inter, sans-serif",
            "heading_font": "Inter, sans-serif",
            "base_size": "16px",
            "scale_ratio": 1.25,
        },
        "spacing": {
            "base_unit": "4px",
            "scale_ratio": 2,
        },
        "border_radius": {
            "small": "4px",
            "medium": "8px",
            "large": "16px",
            "round": "50%",
        }
    }
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def load_design_system_from_file(self, file_path: str = "design_system.json") -> Dict[str, Any]:
        """Load design system from a JSON file if it exists, otherwise return default"""
        path = Path(file_path)
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return self.DEFAULT_DESIGN_SYSTEM

    def save_design_system_to_file(self, design_system: Dict[str, Any], file_path: str = "design_system.json") -> None:
        """Save design system to a JSON file"""
        with open(file_path, "w") as f:
            json.dump(design_system, f, indent=2)


settings = Settings()
```

### 2. Database Setup (app/core/database.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3. Authentication (app/core/security.py)

```python
from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 4. Database Models

#### a. Design System Models (app/models/design.py)

```python
from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class DesignSystem(Base):
    __tablename__ = "design_systems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    config = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<DesignSystem {self.name}>"
```

#### b. Dynamic Data Models (app/models/data.py)

```python
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Many-to-many relationship table for tags
data_tags = Table(
    "data_tags",
    Base.metadata,
    Column("data_id", Integer, ForeignKey("dynamic_data.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    data_items = relationship("DynamicData", secondary=data_tags, back_populates="tags")

class DynamicData(Base):
    __tablename__ = "dynamic_data"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    tags = relationship("Tag", secondary=data_tags, back_populates="data_items")

    def __repr__(self):
        return f"<DynamicData {self.title}>"
```

#### c. Projects Models (app/models/projects.py)

```python
from sqlalchemy import Column, String, ARRAY, Text
from app.core.database import Base

class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    image = Column(String, nullable=False)
    technologies = Column(ARRAY(String), nullable=False)
    link = Column(String, nullable=False)
    github = Column(String, nullable=True)
    appStore = Column(String, nullable=True)
    playStore = Column(String, nullable=True)
    achievements = Column(ARRAY(String), nullable=False)
```

#### d. Experiences Models (app/models/experiences.py)

```python
from sqlalchemy import Column, String, ARRAY, Text
from app.core.database import Base

class ExperienceModel(Base):
    __tablename__ = "experiences"

    id = Column(String, primary_key=True)
    role = Column(String, nullable=False)
    company = Column(String, nullable=False)
    period = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    achievements = Column(ARRAY(String), nullable=False)
    projects = Column(ARRAY(String), nullable=False)
    color = Column(String, nullable=False)
```

### 5. Pydantic Schemas

#### a. Design System Schemas (app/schemas/design.py)

```python
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ColorScheme(BaseModel):
    primary: str = Field(..., description="Primary color hex code", example="#8B5CF6")
    secondary: str = Field(..., description="Secondary color hex code", example="#D946EF")
    accent: str = Field(..., description="Accent color hex code", example="#F97316")
    background: str = Field(..., description="Background color hex code", example="#FFFFFF")
    text: str = Field(..., description="Text color hex code", example="#222222")
    error: str = Field(..., description="Error color hex code", example="#EA384C")
    success: str = Field(..., description="Success color hex code", example="#10B981")
    warning: str = Field(..., description="Warning color hex code", example="#F59E0B")
    info: str = Field(..., description="Info color hex code", example="#0EA5E9")

class DarkModeColors(BaseModel):
    background: str = Field(..., description="Dark mode background color", example="#1A1F2C")
    text: str = Field(..., description="Dark mode text color", example="#FFFFFF")
    primary: str = Field(..., description="Dark mode primary color", example="#9B87F5")

class Typography(BaseModel):
    font_family: str = Field(..., description="Main font family", example="Inter, sans-serif")
    heading_font: str = Field(..., description="Heading font family", example="Inter, sans-serif")
    base_size: str = Field(..., description="Base font size", example="16px")
    scale_ratio: float = Field(..., description="Typography scale ratio", example=1.25)

class Spacing(BaseModel):
    base_unit: str = Field(..., description="Base spacing unit", example="4px")
    scale_ratio: float = Field(..., description="Spacing scale ratio", example=2)

class BorderRadius(BaseModel):
    small: str = Field(..., description="Small border radius", example="4px")
    medium: str = Field(..., description="Medium border radius", example="8px")
    large: str = Field(..., description="Large border radius", example="16px")
    round: str = Field(..., description="Round border radius", example="50%")

class DesignSystemBase(BaseModel):
    name: str = Field(..., description="Name of the design system", example="Default Theme")
    colors: ColorScheme
    dark_mode: DarkModeColors
    typography: Typography
    spacing: Spacing
    border_radius: BorderRadius

class DesignSystemCreate(DesignSystemBase):
    pass

class DesignSystemUpdate(BaseModel):
    name: Optional[str] = None
    colors: Optional[ColorScheme] = None
    dark_mode: Optional[DarkModeColors] = None
    typography: Optional[Typography] = None
    spacing: Optional[Spacing] = None
    border_radius: Optional[BorderRadius] = None

class DesignSystemInDB(DesignSystemBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class DesignSystemResponse(DesignSystemInDB):
    pass
```

#### b. Data Schemas (app/schemas/data.py)

```python
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TagBase(BaseModel):
    name: str = Field(..., description="Tag name", example="product")

class TagCreate(TagBase):
    pass

class TagInDB(TagBase):
    id: int

    class Config:
        orm_mode = True

class DynamicDataBase(BaseModel):
    title: str = Field(..., description="Title of the data item", example="Product Features")
    description: Optional[str] = Field(None, description="Description of the data item")
    content: Dict[str, Any] = Field(..., description="Dynamic JSON content")

class DynamicDataCreate(DynamicDataBase):
    tags: List[str] = Field(default=[], description="List of tag names to associate with the data")

class DynamicDataUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class DynamicDataInDB(DynamicDataBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    tags: List[TagInDB] = []

    class Config:
        orm_mode = True

class DynamicDataResponse(DynamicDataInDB):
    pass

class DynamicDataList(BaseModel):
    data: List[DynamicDataResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
```

#### c. Projects Schemas (app/schemas/projects.py)

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    title: str
    description: str
    image: str
    technologies: List[str]
    link: str
    github: Optional[str] = None
    appStore: Optional[str] = None
    playStore: Optional[str] = None
    achievements: List[str]

class ProjectCreate(ProjectBase):
    id: str

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    technologies: Optional[List[str]] = None
    link: Optional[str] = None
    github: Optional[str] = None
    appStore: Optional[str] = None
    playStore: Optional[str] = None
    achievements: Optional[List[str]] = None

class Project(ProjectBase):
    id: str

    class Config:
        orm_mode = True
```

#### d. Experiences Schemas (app/schemas/experiences.py)

```python
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
```

### 6. CRUD Operations

#### a. Design System CRUD (app/crud/design.py)

*(Same as previous implementation – no changes.)*

#### b. Data CRUD (app/crud/data.py)

*(Same as previous implementation – no changes.)*

#### c. Projects CRUD (app/crud/projects.py)

```python
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
```

#### d. Experiences CRUD (app/crud/experiences.py)

```python
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
```

### 7. API Routes

#### a. Design System Routes (app/api/routes/design.py)

```python
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
def get_color_scheme(db: Session = Depends(get_db)):
    """
    Get the current color scheme from the active design system
    """
    design_system = design_crud.get_active_design_system(db)
    if not design_system:
        from app.core.config import settings
        return settings.DEFAULT_DESIGN_SYSTEM["colors"]
    return design_system.config["colors"]

@router.put("/color-scheme", response_model=ColorScheme)
def update_color_scheme(color_scheme: ColorScheme, db: Session = Depends(get_db)):
    """
    Update the color scheme of the active design system
    """
    design_system = design_crud.get_active_design_system(db)
    if not design_system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active design system found"
        )
    update_data = DesignSystemUpdate(**{"colors": color_scheme.dict()})
    updated = design_crud.update_design_system(db, design_id=design_system.id, design_system=update_data)
    return updated.config["colors"]

# Other design system endpoints (list, get by id, create, update, activate, delete) remain unchanged.
```

#### b. Projects Routes (app/api/routes/projects.py)

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import projects as projects_crud
from app.schemas.projects import Project, ProjectCreate, ProjectUpdate

router = APIRouter()

@router.get("/", response_model=List[Project])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all projects
    """
    return projects_crud.get_projects(db, skip=skip, limit=limit)

@router.get("/{project_id}", response_model=Project)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """
    Get a specific project by ID
    """
    project = projects_crud.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new project
    """
    return projects_crud.create_project(db, project=project)

@router.put("/{project_id}", response_model=Project)
def update_project(project_id: str, project: ProjectUpdate, db: Session = Depends(get_db)):
    """
    Update a project
    """
    db_project = projects_crud.update_project(db, project_id=project_id, project=project)
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return db_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """
    Delete a project
    """
    success = projects_crud.delete_project(db, project_id=project_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return None
```

#### c. Experiences Routes (app/api/routes/experiences.py)

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import experiences as experiences_crud
from app.schemas.experiences import Experience, ExperienceCreate, ExperienceUpdate

router = APIRouter()

@router.get("/", response_model=List[Experience])
def get_experiences(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all work experiences
    """
    return experiences_crud.get_experiences(db, skip=skip, limit=limit)

@router.get("/{experience_id}", response_model=Experience)
def get_experience(experience_id: str, db: Session = Depends(get_db)):
    """
    Get a specific experience by ID
    """
    experience = experiences_crud.get_experience(db, experience_id=experience_id)
    if not experience:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
    return experience

@router.post("/", response_model=Experience, status_code=status.HTTP_201_CREATED)
def create_experience(experience: ExperienceCreate, db: Session = Depends(get_db)):
    """
    Create a new work experience
    """
    return experiences_crud.create_experience(db, experience=experience)

@router.put("/{experience_id}", response_model=Experience)
def update_experience(experience_id: str, experience: ExperienceUpdate, db: Session = Depends(get_db)):
    """
    Update a work experience
    """
    db_experience = experiences_crud.update_experience(db, experience_id=experience_id, experience=experience)
    if not db_experience:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
    return db_experience

@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(experience_id: str, db: Session = Depends(get_db)):
    """
    Delete a work experience
    """
    success = experiences_crud.delete_experience(db, experience_id=experience_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
    return None
```

#### d. Data Routes (app/api/routes/data.py)

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import data as data_crud
from app.schemas.data import DynamicDataCreate, DynamicDataUpdate, DynamicDataResponse, DynamicDataList

router = APIRouter()

@router.post("/", response_model=DynamicDataResponse, status_code=status.HTTP_201_CREATED)
def create_data_item(data_item: DynamicDataCreate, db: Session = Depends(get_db)):
    """
    Create a new dynamic data item
    """
    return data_crud.create_data_item(db=db, data_item=data_item)

@router.get("/", response_model=DynamicDataList)
def read_data_items(skip: int = 0, limit: int = 100, tag: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Retrieve all dynamic data items with optional filtering by tag
    """
    result = data_crud.get_data_items(db, skip=skip, limit=limit, tag=tag)
    return result

@router.get("/search", response_model=DynamicDataList)
def search_data_items(q: str = Query(..., description="Search query string"), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Search for dynamic data items by title or description
    """
    result = data_crud.search_data_items(db, query=q, skip=skip, limit=limit)
    return result

@router.get("/{data_id}", response_model=DynamicDataResponse)
def read_data_item(data_id: int, db: Session = Depends(get_db)):
    """
    Get a specific dynamic data item by ID
    """
    data_item = data_crud.get_data_item(db, data_id=data_id)
    if not data_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data item not found")
    return data_item

@router.put("/{data_id}", response_model=DynamicDataResponse)
def update_data_item(data_id: int, data_item: DynamicDataUpdate, db: Session = Depends(get_db)):
    """
    Update a dynamic data item
    """
    db_data_item = data_crud.update_data_item(db, data_id=data_id, data_item=data_item)
    if not db_data_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data item not found")
    return db_data_item

@router.delete("/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data_item(data_id: int, db: Session = Depends(get_db)):
    """
    Delete a dynamic data item
    """
    success = data_crud.delete_data_item(db, data_id=data_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data item not found")
    return None
```

#### e. API Dependencies (app/api/deps.py)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
```

#### f. Color Utilities (app/utils/color_utils.py)

```python
from typing import Tuple, Dict, Any
import re

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        r = int(hex_color[0] + hex_color[0], 16)
        g = int(hex_color[1] + hex_color[1], 16)
        b = int(hex_color[2] + hex_color[2], 16)
    else:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    return (r, g, b)

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"

def darken_color(hex_color: str, factor: float = 0.2) -> str:
    r, g, b = hex_to_rgb(hex_color)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return rgb_to_hex((r, g, b))

def lighten_color(hex_color: str, factor: float = 0.2) -> str:
    r, g, b = hex_to_rgb(hex_color)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return rgb_to_hex((r, g, b))

def generate_color_palette(primary_color: str) -> Dict[str, str]:
    palette = {
        "primary": primary_color,
        "primary-light": lighten_color(primary_color, 0.3),
        "primary-dark": darken_color(primary_color, 0.3),
    }
    r, g, b = hex_to_rgb(primary_color)
    complementary = rgb_to_hex((255 - r, 255 - g, 255 - b))
    palette["complementary"] = complementary
    return palette

def validate_hex_color(color: str) -> bool:
    pattern = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    return bool(re.match(pattern, color))

def generate_css_variables(design_system: Dict[str, Any]) -> str:
    css = ":root {\n"
    for key, value in design_system["colors"].items():
        css += f"  --color-{key}: {value};\n"
    for key, value in design_system["dark_mode"].items():
        css += f"  --dark-{key}: {value};\n"
    for key, value in design_system["typography"].items():
        css += f"  --typography-{key.replace('_', '-')}: {value};\n"
    for key, value in design_system["spacing"].items():
        css += f"  --spacing-{key.replace('_', '-')}: {value};\n"
    for key, value in design_system["border_radius"].items():
        css += f"  --radius-{key}: {value};\n"
    css += "}\n"
    css += "\n@media (prefers-color-scheme: dark) {\n"
    css += "  :root {\n"
    css += f"    --color-background: {design_system['dark_mode']['background']};\n"
    css += f"    --color-text: {design_system['dark_mode']['text']};\n"
    css += f"    --color-primary: {design_system['dark_mode']['primary']};\n"
    css += "  }\n"
    css += "}\n"
    return css
```

### 8. Main FastAPI Application (app/main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import design, projects, experiences, data
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(design.router, prefix=f"{settings.API_V1_STR}/design", tags=["design"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(experiences.router, prefix=f"{settings.API_V1_STR}/experiences", tags=["experiences"])
app.include_router(data.router, prefix=f"{settings.API_V1_STR}/data", tags=["data"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Portfolio API"}
```

### 9. Docker Configuration

#### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app/

COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml

```yaml
version: '3'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### 10. Python Dependencies (requirements.txt)

```
fastapi>=0.68.0,<0.69.0
uvicorn>=0.15.0,<0.16.0
sqlalchemy>=1.4.0,<1.5.0
pydantic>=1.8.0,<1.9.0
passlib>=1.7.4,<1.8.0
bcrypt>=3.2.0,<3.3.0
python-jose>=3.3.0,<3.4.0
python-multipart>=0.0.5,<0.0.6
alembic>=1.7.4,<1.8.0
psycopg2-binary>=2.9.1,<2.10.0
pytest>=6.2.5,<6.3.0
requests>=2.26.0,<2.27.0
```

### 11. Testing

*(Include your test configuration and test files for data, design, projects, and experiences similar to previous implementations.)*

### 12. How to Run the Project

1. Clone the repository and navigate to the project directory.
2. Create a `.env` file with your environment variables:
   ```
   DATABASE_URL=postgresql://postgres:password@localhost:5432/portfolio_db
   SECRET_KEY=FdsB5oNzKPobJ_3p3In6tU1Xn-MjugfNN8K8ppmPTPQ
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Start the PostgreSQL database:
   ```
   docker-compose up -d db
   ```
5. Run migrations:
   ```
   alembic upgrade head
   ```
6. Start the FastAPI server:
   ```
   uvicorn app.main:app --reload
   ```
7. Access the API at [http://localhost:8000](http://localhost:8000)
8. View the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs)

### 13. API Endpoints

#### Design System Endpoints

- `GET /api/v1/design/color-scheme`: Get the current color scheme  
- `PUT /api/v1/design/color-scheme`: Update the current color scheme  
- Other endpoints: list, get by id, create, update, activate, delete

#### Projects Endpoints

- `GET /api/v1/projects`: Get all projects  
- `GET /api/v1/projects/{project_id}`: Get a specific project by ID  
- `POST /api/v1/projects`: Create a new project  
- `PUT /api/v1/projects/{project_id}`: Update a project  
- `DELETE /api/v1/projects/{project_id}`: Delete a project

#### Experiences Endpoints

- `GET /api/v1/experiences`: Get all work experiences  
- `GET /api/v1/experiences/{experience_id}`: Get a specific experience by ID  
- `POST /api/v1/experiences`: Create a new work experience  
- `PUT /api/v1/experiences/{experience_id}`: Update a work experience  
- `DELETE /api/v1/experiences/{experience_id}`: Delete a work experience

### 14. Frontend Integration

Example to fetch the design system’s color scheme:

```typescript
async function fetchAndApplyDesignSystem() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/design/color-scheme');
    const colorScheme = await response.json();
    // Apply color scheme to your CSS variables or theme provider
  } catch (error) {
    console.error('Error fetching color scheme:', error);
  }
}
```
```

---

### collection.json

```json
{
  "info": {
    "name": "Design System API Collection",
    "description": "Postman collection for the Design System API backend.",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Active Design System",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/api/v1/design/active",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "design",
            "active"
          ]
        }
      }
    },
    {
      "name": "List All Design Systems",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/api/v1/design/",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "design"
          ]
        }
      }
    },
    {
      "name": "Create Design System",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"Default Theme\",\n  \"colors\": {\n    \"primary\": \"#8B5CF6\",\n    \"secondary\": \"#D946EF\",\n    \"accent\": \"#F97316\",\n    \"background\": \"#FFFFFF\",\n    \"text\": \"#222222\",\n    \"error\": \"#EA384C\",\n    \"success\": \"#10B981\",\n    \"warning\": \"#F59E0B\",\n    \"info\": \"#0EA5E9\"\n  },\n  \"dark_mode\": {\n    \"background\": \"#1A1F2C\",\n    \"text\": \"#FFFFFF\",\n    \"primary\": \"#9B87F5\"\n  },\n  \"typography\": {\n    \"font_family\": \"Inter, sans-serif\",\n    \"heading_font\": \"Inter, sans-serif\",\n    \"base_size\": \"16px\",\n    \"scale_ratio\": 1.25\n  },\n  \"spacing\": {\n    \"base_unit\": \"4px\",\n    \"scale_ratio\": 2\n  },\n  \"border_radius\": {\n    \"small\": \"4px\",\n    \"medium\": \"8px\",\n    \"large\": \"16px\",\n    \"round\": \"50%\"\n  }\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/api/v1/design/",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "design"
          ]
        }
      }
    },
    {
      "name": "Update Design System Color Scheme",
      "request": {
        "method": "PUT",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"primary\": \"#FF0000\",\n  \"secondary\": \"#00FF00\",\n  \"accent\": \"#0000FF\",\n  \"background\": \"#FFFFFF\",\n  \"text\": \"#000000\",\n  \"error\": \"#FF0000\",\n  \"success\": \"#00FF00\",\n  \"warning\": \"#FFFF00\",\n  \"info\": \"#0000FF\"\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/api/v1/design/color-scheme",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "design",
            "color-scheme"
          ]
        }
      }
    },
    {
      "name": "List All Projects",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/api/v1/projects",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "projects"
          ]
        }
      }
    },
    {
      "name": "Get Project by ID",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/api/v1/projects/1",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "projects",
            "1"
          ]
        }
      }
    },
    {
      "name": "Create Project",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"id\": \"1\",\n  \"title\": \"New Project\",\n  \"description\": \"Project description\",\n  \"image\": \"https://example.com/image.png\",\n  \"technologies\": [\"MERN\", \"Python\"],\n  \"link\": \"https://example.com\",\n  \"github\": \"https://github.com/example\",\n  \"appStore\": \"\",\n  \"playStore\": \"\",\n  \"achievements\": [\"Achievement 1\", \"Achievement 2\"]\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/api/v1/projects",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "projects"
          ]
        }
      }
    },
    {
      "name": "Update Project",
      "request": {
        "method": "PUT",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"title\": \"Updated Project Title\"\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/api/v1/projects/1",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "projects",
            "1"
          ]
        }
      }
    },
    {
      "name": "Delete Project",
      "request": {
        "method": "DELETE",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/api/v1/projects/1",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "projects",
            "1"
          ]
        }
      }
    },
    {
      "name": "List All Experiences",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/api/v1/experiences",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "experiences"
          ]
        }
      }
    },
    {
      "name": "Get Experience by ID",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/api/v1/experiences/1",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "experiences",
            "1"
          ]
        }
      }
    },
    {
      "name": "Create Experience",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"id\": \"1\",\n  \"role\": \"Developer\",\n  \"company\": \"Example Corp\",\n  \"period\": \"2021-2022\",\n  \"description\": \"Worked on various projects.\",\n  \"achievements\": [\"Achievement 1\", \"Achievement 2\"],\n  \"projects\": [\"1\"],\n  \"color\": \"#FF0000\"\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/api/v1/experiences",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "experiences"
          ]
        }
      }
    },
    {
      "name": "Update Experience",
      "request": {
        "method": "PUT",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"role\": \"Senior Developer\"\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/api/v1/experiences/1",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "experiences",
            "1"
          ]
        }
      }
    },
    {
      "name": "Delete Experience",
      "request": {
        "method": "DELETE",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/api/v1/experiences/1",
          "host": [
            "{{baseUrl}}"
          ],
          "path": [
            "api",
            "v1",
            "experiences",
            "1"
          ]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8000"
    }
  ]
}
```

---

You can now use your `create_files.py` script (or any similar tool) to automatically create these files in your project directory. The `backend.md` file contains comprehensive documentation of your backend implementation, and `collection.json` provides a ready-to-import Postman collection for testing your endpoints.