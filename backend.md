
# Dynamic Backend with Integrated Design System

This document outlines a complete implementation of a Python-based backend that supports dynamic data updates and a configurable design system.

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
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Application configuration
│   │   ├── security.py      # Authentication and authorization
│   │   └── database.py      # Database connection management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── data.py      # Dynamic data CRUD endpoints
│   │   │   └── design.py    # Design system endpoints
│   │   └── deps.py          # Dependency injection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── data.py          # Dynamic data models
│   │   └── design.py        # Design system models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── data.py          # Pydantic models for data
│   │   └── design.py        # Pydantic models for design system
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py          # Base CRUD operations
│   │   ├── data.py          # Dynamic data CRUD operations
│   │   └── design.py        # Design system CRUD operations
│   └── utils/
│       ├── __init__.py
│       └── color_utils.py   # Utilities for color manipulation
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   ├── test_data.py         # Tests for data endpoints
│   └── test_design.py       # Tests for design system endpoints
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
└── README.md                # Project documentation
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
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 4. Database Models (app/models/design.py)

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

### 5. Database Models (app/models/data.py)

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

### 6. Pydantic Schemas (app/schemas/design.py)

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

# For API responses
class DesignSystemResponse(DesignSystemInDB):
    pass
```

### 7. Pydantic Schemas (app/schemas/data.py)

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

# For API responses
class DynamicDataResponse(DynamicDataInDB):
    pass

# For listing multiple items
class DynamicDataList(BaseModel):
    data: List[DynamicDataResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
```

### 8. CRUD Operations for Design System (app/crud/design.py)

```python
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
```

### 9. CRUD Operations for Dynamic Data (app/crud/data.py)

```python
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.data import DynamicData, Tag
from app.schemas.data import DynamicDataCreate, DynamicDataUpdate

def get_tag_by_name(db: Session, name: str) -> Optional[Tag]:
    return db.query(Tag).filter(Tag.name == name).first()

def create_tag(db: Session, name: str) -> Tag:
    db_tag = Tag(name=name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def get_or_create_tag(db: Session, name: str) -> Tag:
    tag = get_tag_by_name(db, name)
    if not tag:
        tag = create_tag(db, name)
    return tag

def get_data_item(db: Session, data_id: int) -> Optional[DynamicData]:
    return db.query(DynamicData).filter(DynamicData.id == data_id).first()

def get_data_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    tag: Optional[str] = None
) -> Dict[str, Any]:
    query = db.query(DynamicData)
    
    # Apply tag filter if provided
    if tag:
        query = query.join(DynamicData.tags).filter(Tag.name == tag)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    items = query.offset(skip).limit(limit).all()
    
    # Calculate pages
    page = skip // limit + 1 if limit else 1
    page_size = limit
    total_pages = (total + page_size - 1) // page_size if page_size else 1
    
    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

def create_data_item(db: Session, data_item: DynamicDataCreate) -> DynamicData:
    # Create the data item
    db_data_item = DynamicData(
        title=data_item.title,
        description=data_item.description,
        content=data_item.content
    )
    
    # Add tags
    if data_item.tags:
        for tag_name in data_item.tags:
            tag = get_or_create_tag(db, tag_name)
            db_data_item.tags.append(tag)
    
    db.add(db_data_item)
    db.commit()
    db.refresh(db_data_item)
    return db_data_item

def update_data_item(
    db: Session, data_id: int, data_item: DynamicDataUpdate
) -> Optional[DynamicData]:
    db_data_item = get_data_item(db, data_id)
    if not db_data_item:
        return None
    
    update_data = data_item.dict(exclude_unset=True)
    
    # Update basic fields
    for key in ["title", "description", "content"]:
        if key in update_data:
            setattr(db_data_item, key, update_data[key])
    
    # Update tags if provided
    if "tags" in update_data:
        # Clear existing tags
        db_data_item.tags = []
        
        # Add new tags
        for tag_name in update_data["tags"]:
            tag = get_or_create_tag(db, tag_name)
            db_data_item.tags.append(tag)
    
    db.commit()
    db.refresh(db_data_item)
    return db_data_item

def delete_data_item(db: Session, data_id: int) -> bool:
    db_data_item = get_data_item(db, data_id)
    if not db_data_item:
        return False
    
    db.delete(db_data_item)
    db.commit()
    return True

def search_data_items(
    db: Session, 
    query: str, 
    skip: int = 0, 
    limit: int = 100
) -> Dict[str, Any]:
    # Case-insensitive search in title and description
    search_query = f"%{query}%"
    db_query = db.query(DynamicData).filter(
        (func.lower(DynamicData.title).like(func.lower(search_query))) |
        (func.lower(DynamicData.description).like(func.lower(search_query)))
    )
    
    # Get total count
    total = db_query.count()
    
    # Apply pagination
    items = db_query.offset(skip).limit(limit).all()
    
    # Calculate pages
    page = skip // limit + 1 if limit else 1
    page_size = limit
    total_pages = (total + page_size - 1) // page_size if page_size else 1
    
    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }
```

### 10. API Routes for Design System (app/api/routes/design.py)

```python
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import design as design_crud
from app.schemas.design import (
    DesignSystemCreate,
    DesignSystemUpdate,
    DesignSystemResponse
)

router = APIRouter()

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
```

### 11. API Routes for Dynamic Data (app/api/routes/data.py)

```python
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import data as data_crud
from app.schemas.data import (
    DynamicDataCreate,
    DynamicDataUpdate,
    DynamicDataResponse,
    DynamicDataList
)

router = APIRouter()

@router.post("/", response_model=DynamicDataResponse, status_code=status.HTTP_201_CREATED)
def create_data_item(
    data_item: DynamicDataCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new dynamic data item
    """
    return data_crud.create_data_item(db=db, data_item=data_item)

@router.get("/", response_model=DynamicDataList)
def read_data_items(
    skip: int = 0,
    limit: int = 100,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all dynamic data items with optional filtering by tag
    """
    result = data_crud.get_data_items(db, skip=skip, limit=limit, tag=tag)
    return result

@router.get("/search", response_model=DynamicDataList)
def search_data_items(
    q: str = Query(..., description="Search query string"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Search for dynamic data items by title or description
    """
    result = data_crud.search_data_items(db, query=q, skip=skip, limit=limit)
    return result

@router.get("/{data_id}", response_model=DynamicDataResponse)
def read_data_item(
    data_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific dynamic data item by ID
    """
    data_item = data_crud.get_data_item(db, data_id=data_id)
    if not data_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data item not found"
        )
    return data_item

@router.put("/{data_id}", response_model=DynamicDataResponse)
def update_data_item(
    data_id: int,
    data_item: DynamicDataUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a dynamic data item
    """
    db_data_item = data_crud.update_data_item(
        db, data_id=data_id, data_item=data_item
    )
    if not db_data_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data item not found"
        )
    return db_data_item

@router.delete("/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data_item(
    data_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a dynamic data item
    """
    success = data_crud.delete_data_item(db, data_id=data_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data item not found"
        )
    return None
```

### 12. API Dependencies (app/api/deps.py)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

# This is a simplified version without full auth implementation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# You would expand this with actual auth logic in a real application
```

### 13. Color Utilities (app/utils/color_utils.py)

```python
from typing import Tuple, Dict, Any
import re

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color code to RGB tuple"""
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Parse hex values
    if len(hex_color) == 3:
        # Handle shorthand hex (#RGB)
        r = int(hex_color[0] + hex_color[0], 16)
        g = int(hex_color[1] + hex_color[1], 16)
        b = int(hex_color[2] + hex_color[2], 16)
    else:
        # Handle full hex (#RRGGBB)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    
    return (r, g, b)

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color code"""
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"

def darken_color(hex_color: str, factor: float = 0.2) -> str:
    """Darken a color by the given factor (0-1)"""
    r, g, b = hex_to_rgb(hex_color)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return rgb_to_hex((r, g, b))

def lighten_color(hex_color: str, factor: float = 0.2) -> str:
    """Lighten a color by the given factor (0-1)"""
    r, g, b = hex_to_rgb(hex_color)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return rgb_to_hex((r, g, b))

def generate_color_palette(primary_color: str) -> Dict[str, str]:
    """
    Generate a color palette based on a primary color
    Returns primary, primary-light, primary-dark, and complementary colors
    """
    palette = {
        "primary": primary_color,
        "primary-light": lighten_color(primary_color, 0.3),
        "primary-dark": darken_color(primary_color, 0.3),
    }
    
    # Generate complementary color (opposite on the color wheel)
    r, g, b = hex_to_rgb(primary_color)
    complementary = rgb_to_hex((255 - r, 255 - g, 255 - b))
    palette["complementary"] = complementary
    
    return palette

def validate_hex_color(color: str) -> bool:
    """Validate if string is a proper hex color code"""
    pattern = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    return bool(re.match(pattern, color))

def generate_css_variables(design_system: Dict[str, Any]) -> str:
    """Generate CSS variables from a design system configuration"""
    css = ":root {\n"
    
    # Color variables
    for key, value in design_system["colors"].items():
        css += f"  --color-{key}: {value};\n"
    
    # Dark mode variables
    for key, value in design_system["dark_mode"].items():
        css += f"  --dark-{key}: {value};\n"
    
    # Typography variables
    for key, value in design_system["typography"].items():
        css += f"  --typography-{key.replace('_', '-')}: {value};\n"
    
    # Spacing variables
    for key, value in design_system["spacing"].items():
        css += f"  --spacing-{key.replace('_', '-')}: {value};\n"
    
    # Border radius variables
    for key, value in design_system["border_radius"].items():
        css += f"  --radius-{key}: {value};\n"
    
    css += "}\n"
    
    # Add dark mode
    css += "\n@media (prefers-color-scheme: dark) {\n"
    css += "  :root {\n"
    css += f"    --color-background: {design_system['dark_mode']['background']};\n"
    css += f"    --color-text: {design_system['dark_mode']['text']};\n"
    css += f"    --color-primary: {design_system['dark_mode']['primary']};\n"
    css += "  }\n"
    css += "}\n"
    
    return css
```

### 14. Main FastAPI Application (app/main.py)

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse

from app.api.routes import data, design
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(data.router, prefix=f"{settings.API_V1_STR}/data", tags=["data"])
app.include_router(design.router, prefix=f"{settings.API_V1_STR}/design", tags=["design"])

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Design System API</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2rem;
                    line-height: 1.6;
                }
                a {
                    color: #0066cc;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                .endpoints {
                    background-color: #f5f5f5;
                    padding: 1rem;
                    border-radius: 0.5rem;
                }
            </style>
        </head>
        <body>
            <h1>Design System API</h1>
            <p>Welcome to the Design System API. This API provides endpoints for managing design systems and dynamic data.</p>
            
            <h2>Documentation</h2>
            <p>
                <a href="/docs">Swagger UI</a> - Interactive API documentation
                <br>
                <a href="/redoc">ReDoc</a> - Alternative API documentation
            </p>
            
            <h2>Main Endpoints</h2>
            <div class="endpoints">
                <h3>Design System</h3>
                <ul>
                    <li><code>GET /api/v1/design/</code> - List all design systems</li>
                    <li><code>GET /api/v1/design/active</code> - Get the active design system</li>
                    <li><code>POST /api/v1/design/</code> - Create a new design system</li>
                    <li><code>PUT /api/v1/design/{id}</code> - Update a design system</li>
                    <li><code>POST /api/v1/design/{id}/activate</code> - Activate a design system</li>
                </ul>
                
                <h3>Dynamic Data</h3>
                <ul>
                    <li><code>GET /api/v1/data/</code> - List all data items</li>
                    <li><code>GET /api/v1/data/search?q={query}</code> - Search data items</li>
                    <li><code>POST /api/v1/data/</code> - Create a new data item</li>
                    <li><code>PUT /api/v1/data/{id}</code> - Update a data item</li>
                    <li><code>DELETE /api/v1/data/{id}</code> - Delete a data item</li>
                </ul>
            </div>
        </body>
    </html>
    """

@app.get("/api/v1/css", response_class=FileResponse)
async def get_css():
    """Generate and return CSS variables based on the active design system"""
    # In a real application, you would generate this dynamically
    # For now, we'll return a static CSS file
    return FileResponse("app/static/css/styles.css")
```

### 15. Docker Configuration (Dockerfile)

```dockerfile
FROM python:3.9-slim

WORKDIR /app/

COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 16. Docker Compose Configuration (docker-compose.yml)

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
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
      - SECRET_KEY=your-secret-key-change-in-production
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

### 17. Python Dependencies (requirements.txt)

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

## Testing

### 1. Test Configuration (tests/conftest.py)

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a database session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
```

### 2. Data API Tests (tests/test_data.py)

```python
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.crud.data import create_data_item
from app.schemas.data import DynamicDataCreate

def test_create_data_item(client: TestClient, db: Session):
    # Test data
    data = {
        "title": "Test Data",
        "description": "Test description",
        "content": {"key": "value"},
        "tags": ["test", "example"]
    }
    
    # Create data item
    response = client.post("/api/v1/data/", json=data)
    
    # Check response
    assert response.status_code == 201
    created_data = response.json()
    assert created_data["title"] == data["title"]
    assert created_data["description"] == data["description"]
    assert created_data["content"] == data["content"]
    
    # Check that tags were created
    assert len(created_data["tags"]) == 2
    assert created_data["tags"][0]["name"] == "test"
    assert created_data["tags"][1]["name"] == "example"

def test_read_data_items(client: TestClient, db: Session):
    # Create test data
    data1 = DynamicDataCreate(
        title="Test Data 1",
        description="Description 1",
        content={"key": "value1"},
        tags=["tag1", "tag2"]
    )
    create_data_item(db, data1)
    
    data2 = DynamicDataCreate(
        title="Test Data 2",
        description="Description 2",
        content={"key": "value2"},
        tags=["tag2", "tag3"]
    )
    create_data_item(db, data2)
    
    # Test listing all data items
    response = client.get("/api/v1/data/")
    assert response.status_code == 200
    
    result = response.json()
    assert result["total"] == 2
    assert len(result["data"]) == 2
    
    # Test filtering by tag
    response = client.get("/api/v1/data/?tag=tag1")
    assert response.status_code == 200
    
    result = response.json()
    assert result["total"] == 1
    assert result["data"][0]["title"] == "Test Data 1"

def test_search_data_items(client: TestClient, db: Session):
    # Create test data
    data1 = DynamicDataCreate(
        title="Search Test",
        description="This is a search test",
        content={"key": "value1"},
        tags=["search"]
    )
    create_data_item(db, data1)
    
    data2 = DynamicDataCreate(
        title="Another Test",
        description="This contains search keyword",
        content={"key": "value2"},
        tags=["other"]
    )
    create_data_item(db, data2)
    
    # Test search
    response = client.get("/api/v1/data/search?q=search")
    assert response.status_code == 200
    
    result = response.json()
    assert result["total"] == 2
    
    # More specific search
    response = client.get("/api/v1/data/search?q=Search%20Test")
    assert response.status_code == 200
    
    result = response.json()
    assert result["total"] == 1
    assert result["data"][0]["title"] == "Search Test"

def test_update_data_item(client: TestClient, db: Session):
    # Create test data
    data = DynamicDataCreate(
        title="Original Title",
        description="Original description",
        content={"key": "original"},
        tags=["original"]
    )
    created = create_data_item(db, data)
    
    # Update data
    update_data = {
        "title": "Updated Title",
        "content": {"key": "updated"},
        "tags": ["updated", "new"]
    }
    
    response = client.put(f"/api/v1/data/{created.id}", json=update_data)
    assert response.status_code == 200
    
    updated = response.json()
    assert updated["title"] == "Updated Title"
    assert updated["description"] == "Original description"  # Not updated
    assert updated["content"] == {"key": "updated"}
    
    # Check tags
    assert len(updated["tags"]) == 2
    tag_names = [tag["name"] for tag in updated["tags"]]
    assert "updated" in tag_names
    assert "new" in tag_names
    assert "original" not in tag_names  # Old tag removed

def test_delete_data_item(client: TestClient, db: Session):
    # Create test data
    data = DynamicDataCreate(
        title="To be deleted",
        description="This will be deleted",
        content={"key": "value"},
        tags=["delete"]
    )
    created = create_data_item(db, data)
    
    # Delete data
    response = client.delete(f"/api/v1/data/{created.id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get(f"/api/v1/data/{created.id}")
    assert response.status_code == 404
```

### 3. Design System API Tests (tests/test_design.py)

```python
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.crud.design import create_design_system
from app.schemas.design import DesignSystemCreate

def test_create_design_system(client: TestClient, db: Session):
    # Test data
    design_data = {
        "name": "Test Theme",
        "colors": {
            "primary": "#FF0000",
            "secondary": "#00FF00",
            "accent": "#0000FF",
            "background": "#FFFFFF",
            "text": "#000000",
            "error": "#FF0000",
            "success": "#00FF00",
            "warning": "#FFFF00",
            "info": "#0000FF"
        },
        "dark_mode": {
            "background": "#000000",
            "text": "#FFFFFF",
            "primary": "#FF0000"
        },
        "typography": {
            "font_family": "Arial, sans-serif",
            "heading_font": "Arial, sans-serif",
            "base_size": "16px",
            "scale_ratio": 1.25
        },
        "spacing": {
            "base_unit": "4px",
            "scale_ratio": 2
        },
        "border_radius": {
            "small": "4px",
            "medium": "8px",
            "large": "16px",
            "round": "50%"
        }
    }
    
    # Create design system
    response = client.post("/api/v1/design/", json=design_data)
    
    # Check response
    assert response.status_code == 201
    created_design = response.json()
    assert created_design["name"] == design_data["name"]
    assert created_design["colors"]["primary"] == design_data["colors"]["primary"]
    assert created_design["typography"]["font_family"] == design_data["typography"]["font_family"]

def test_read_design_systems(client: TestClient, db: Session):
    # Create test data
    design1 = DesignSystemCreate(
        name="Theme 1",
        colors={
            "primary": "#FF0000",
            "secondary": "#00FF00",
            "accent": "#0000FF",
            "background": "#FFFFFF",
            "text": "#000000",
            "error": "#FF0000",
            "success": "#00FF00",
            "warning": "#FFFF00",
            "info": "#0000FF"
        },
        dark_mode={
            "background": "#000000",
            "text": "#FFFFFF",
            "primary": "#FF0000"
        },
        typography={
            "font_family": "Arial, sans-serif",
            "heading_font": "Arial, sans-serif",
            "base_size": "16px",
            "scale_ratio": 1.25
        },
        spacing={
            "base_unit": "4px",
            "scale_ratio": 2
        },
        border_radius={
            "small": "4px",
            "medium": "8px",
            "large": "16px",
            "round": "50%"
        }
    )
    create_design_system(db, design1)
    
    design2 = DesignSystemCreate(
        name="Theme 2",
        colors={
            "primary": "#0000FF",
            "secondary": "#00FF00",
            "accent": "#FF0000",
            "background": "#EEEEEE",
            "text": "#111111",
            "error": "#FF0000",
            "success": "#00FF00",
            "warning": "#FFFF00",
            "info": "#0000FF"
        },
        dark_mode={
            "background": "#111111",
            "text": "#EEEEEE",
            "primary": "#0000FF"
        },
        typography={
            "font_family": "Helvetica, sans-serif",
            "heading_font": "Helvetica, sans-serif",
            "base_size": "14px",
            "scale_ratio": 1.2
        },
        spacing={
            "base_unit": "8px",
            "scale_ratio": 1.5
        },
        border_radius={
            "small": "2px",
            "medium": "4px",
            "large": "8px",
            "round": "50%"
        }
    )
    create_design_system(db, design2)
    
    # Test listing all design systems
    response = client.get("/api/v1/design/")
    assert response.status_code == 200
    
    result = response.json()
    assert len(result) == 2
    assert result[0]["name"] == "Theme 1"
    assert result[1]["name"] == "Theme 2"

def test_activate_design_system(client: TestClient, db: Session):
    # Create two design systems
    design1 = DesignSystemCreate(
        name="Default Theme",
        colors={
            "primary": "#FF0000",
            "secondary": "#00FF00",
            "accent": "#0000FF",
            "background": "#FFFFFF",
            "text": "#000000",
            "error": "#FF0000",
            "success": "#00FF00",
            "warning": "#FFFF00",
            "info": "#0000FF"
        },
        dark_mode={
            "background": "#000000",
            "text": "#FFFFFF",
            "primary": "#FF0000"
        },
        typography={
            "font_family": "Arial, sans-serif",
            "heading_font": "Arial, sans-serif",
            "base_size": "16px",
            "scale_ratio": 1.25
        },
        spacing={
            "base_unit": "4px",
            "scale_ratio": 2
        },
        border_radius={
            "small": "4px",
            "medium": "8px",
            "large": "16px",
            "round": "50%"
        }
    )
    created1 = create_design_system(db, design1)
    
    design2 = DesignSystemCreate(
        name="Alternative Theme",
        colors={
            "primary": "#0000FF",
            "secondary": "#00FF00",
            "accent": "#FF0000",
            "background": "#EEEEEE",
            "text": "#111111",
            "error": "#FF0000",
            "success": "#00FF00",
            "warning": "#FFFF00",
            "info": "#0000FF"
        },
        dark_mode={
            "background": "#111111",
            "text": "#EEEEEE",
            "primary": "#0000FF"
        },
        typography={
            "font_family": "Helvetica, sans-serif",
            "heading_font": "Helvetica, sans-serif",
            "base_size": "14px",
            "scale_ratio": 1.2
        },
        spacing={
            "base_unit": "8px",
            "scale_ratio": 1.5
        },
        border_radius={
            "small": "2px",
            "medium": "4px",
            "large": "8px",
            "round": "50%"
        }
    )
    created2 = create_design_system(db, design2)
    
    # Activate the second theme
    response = client.post(f"/api/v1/design/{created2.id}/activate")
    assert response.status_code == 200
    
    # Check that it's active
    response = client.get("/api/v1/design/active")
    assert response.status_code == 200
    active = response.json()
    assert active["id"] == created2.id
    assert active["name"] == "Alternative Theme"
    
    # Now activate the first theme
    response = client.post(f"/api/v1/design/{created1.id}/activate")
    assert response.status_code == 200
    
    # Check that it's now active
    response = client.get("/api/v1/design/active")
    assert response.status_code == 200
    active = response.json()
    assert active["id"] == created1.id
    assert active["name"] == "Default Theme"

def test_update_design_system(client: TestClient, db: Session):
    # Create a design system
    design = DesignSystemCreate(
        name="Original Theme",
        colors={
            "primary": "#FF0000",
            "secondary": "#00FF00",
            "accent": "#0000FF",
            "background": "#FFFFFF",
            "text": "#000000",
            "error": "#FF0000",
            "success": "#00FF00",
            "warning": "#FFFF00",
            "info": "#0000FF"
        },
        dark_mode={
            "background": "#000000",
            "text": "#FFFFFF",
            "primary": "#FF0000"
        },
        typography={
            "font_family": "Arial, sans-serif",
            "heading_font": "Arial, sans-serif",
            "base_size": "16px",
            "scale_ratio": 1.25
        },
        spacing={
            "base_unit": "4px",
            "scale_ratio": 2
        },
        border_radius={
            "small": "4px",
            "medium": "8px",
            "large": "16px",
            "round": "50%"
        }
    )
    created = create_design_system(db, design)
    
    # Update only certain fields
    update_data = {
        "name": "Updated Theme",
        "colors": {
            "primary": "#00FF00",
            "secondary": "#0000FF",
            "accent": "#FF0000",
            "background": "#FFFFFF",
            "text": "#000000",
            "error": "#FF0000",
            "success": "#00FF00",
            "warning": "#FFFF00",
            "info": "#0000FF"
        }
    }
    
    response = client.put(f"/api/v1/design/{created.id}", json=update_data)
    assert response.status_code == 200
    
    updated = response.json()
    assert updated["name"] == "Updated Theme"
    assert updated["colors"]["primary"] == "#00FF00"
    assert updated["colors"]["secondary"] == "#0000FF"
    
    # Check that other fields remain unchanged
    assert updated["typography"]["font_family"] == "Arial, sans-serif"
    assert updated["spacing"]["base_unit"] == "4px"
```

## How to Run the Project

1. Clone the repository and navigate to the project directory.
2. Create a `.env` file with the following environment variables:
   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app
   SECRET_KEY=your-secret-key-change-in-production
   ```
3. Install the dependencies:
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
7. Access the API at http://localhost:8000
8. View the API documentation at http://localhost:8000/docs

## Integration with Frontend

To integrate this backend with your frontend:

1. Use the `/api/v1/design/active` endpoint to fetch the current design system configuration.
2. Apply the configuration to your frontend by setting CSS variables or using a theme provider.
3. Use the dynamic data endpoints to fetch and display content from the backend.

Example frontend code to fetch and apply a design system:

```javascript
async function fetchAndApplyDesignSystem() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/design/active');
    const designSystem = await response.json();
    
    // Apply the design system to the frontend
    applyDesignSystem(designSystem);
  } catch (error) {
    console.error('Failed to fetch design system:', error);
  }
}

function applyDesignSystem(designSystem) {
  const root = document.documentElement;
  
  // Apply colors
  Object.entries(designSystem.colors).forEach(([key, value]) => {
    root.style.setProperty(`--color-${key}`, value);
  });
  
  // Apply dark mode colors
  Object.entries(designSystem.dark_mode).forEach(([key, value]) => {
    root.style.setProperty(`--dark-${key}`, value);
  });
  
  // Apply typography
  Object.entries(designSystem.typography).forEach(([key, value]) => {
    root.style.setProperty(`--typography-${key.replace('_', '-')}`, value);
  });
  
  // Apply spacing
  Object.entries(designSystem.spacing).forEach(([key, value]) => {
    root.style.setProperty(`--spacing-${key.replace('_', '-')}`, value);
  });
  
  // Apply border radius
  Object.entries(designSystem.border_radius).forEach(([key, value]) => {
    root.style.setProperty(`--radius-${key}`, value);
  });
}

// Call this function when the app initializes
fetchAndApplyDesignSystem();
```

## Conclusion

This backend implementation provides a robust foundation for a dynamic data and design system API. It allows for:

1. Creating, updating, and managing design systems with comprehensive theming options
2. Dynamic data management with tagging and search capabilities
3. Secure API access with proper error handling
4. Easy integration with any frontend framework

The modular architecture makes it easy to extend with additional features as needed.
