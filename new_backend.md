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
│   │   │   ├── projects.py  # Projects endpoints
│   │   │   ├── experiences.py # Experiences endpoints
│   │   │   └── design.py    # Design system endpoints
│   │   └── deps.py          # Dependency injection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── projects.py      # Project models
│   │   ├── experiences.py   # Experience models
│   │   └── design.py        # Design system models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── projects.py      # Pydantic models for projects
│   │   ├── experiences.py   # Pydantic models for experiences
│   │   └── design.py        # Pydantic models for design system
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py          # Base CRUD operations
│   │   ├── projects.py      # Projects CRUD operations
│   │   ├── experiences.py   # Experiences CRUD operations
│   │   └── design.py        # Design system CRUD operations
│   └── utils/
│       ├── __init__.py
│       └── color_utils.py   # Utilities for color manipulation
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   ├── test_projects.py     # Tests for projects endpoints
│   ├── test_experiences.py  # Tests for experiences endpoints
│   └── test_design.py       # Tests for design system endpoints
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
└── README.md                # Project documentation
```

// ... keep existing code (Implementation Details section 1-9) 

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

// ... keep existing code (existing design routes)
```

### 11. API Routes for Projects (app/api/routes/projects.py)

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import projects as projects_crud
from app.schemas.projects import (
    Project,
    ProjectCreate,
    ProjectUpdate
)

router = APIRouter()

@router.get("/", response_model=List[Project])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all projects
    """
    return projects_crud.get_projects(db, skip=skip, limit=limit)

@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific project by ID
    """
    project = projects_crud.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new project
    """
    return projects_crud.create_project(db, project=project)

@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: str,
    project: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a project
    """
    db_project = projects_crud.update_project(db, project_id=project_id, project=project)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return db_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a project
    """
    success = projects_crud.delete_project(db, project_id=project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return None
```

### 12. API Routes for Experiences (app/api/routes/experiences.py)

```python
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
```

### 13. Project Models and Schemas (app/models/projects.py)

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

### 14. Project Schemas (app/schemas/projects.py)

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

### 15. Experience Models (app/models/experiences.py)

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

### 16. Experience Schemas (app/schemas/experiences.py)

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

### 17. Main FastAPI Application with Routes Registration (app/main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import design, projects, experiences
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
app.include_router(design.router, prefix=f"{settings.API_V1_STR}/design", tags=["design"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(experiences.router, prefix=f"{settings.API_V1_STR}/experiences", tags=["experiences"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Portfolio API"}
```

// ... keep existing code (remaining implementation details and How to Run the Project section)

## API Endpoints

The backend provides the following key endpoints that are used by the frontend API service:

### Design System Endpoints

- `GET /api/design/color-scheme`: Get the current color scheme
- `PUT /api/design/color-scheme`: Update the current color scheme

### Projects Endpoints

- `GET /api/projects`: Get all projects
- `GET /api/projects/{project_id}`: Get a specific project by ID

### Experiences Endpoints

- `GET /api/experiences`: Get all work experiences

## Frontend Integration

The frontend uses these endpoints through the API service in `src/services/api.ts`. When the backend is not available, the frontend falls back to using the default data defined in the API service.

Example frontend code to fetch data from these endpoints:

```typescript
// Example from src/services/api.ts
export const colorSchemeApi = {
  // Get the current color scheme
  getColorScheme: async (): Promise<ColorScheme> => {
    try {
      const response = await fetchWithTimeout<ColorScheme>(
        `${API_BASE_URL}/design/color-scheme`, 
        { method: "GET" }
      );
      
      if (!response.success) {
        console.warn("Using default color scheme due to API error:", response.error);
        return DEFAULT_COLOR_SCHEME;
      }
      
      return response.data || DEFAULT_COLOR_SCHEME;
    } catch (error) {
      console.error("Failed to fetch color scheme:", error);
      return DEFAULT_COLOR_SCHEME;
    }
  },
  
  // Update the color scheme
  updateColorScheme: async (colorScheme: ColorScheme): Promise<boolean> => {
    try {
      const response = await fetchWithTimeout<ColorScheme>(
        `${API_BASE_URL}/design/color-scheme`,
        {
          method: "PUT",
          body: JSON.stringify(colorScheme),
        }
      );
      
      if (!response.success) {
        toast({
          title: "Failed to update color scheme",
          description: response.error,
          variant: "destructive",
        });
        return false;
      }
      
      toast({
        title: "Color scheme updated",
        description: "The new color scheme has been applied successfully",
      });
      
      return true;
    } catch (error) {
      console.error("Failed to update color scheme:", error);
      toast({
        title: "Failed to update color scheme",
        description: "Could not connect to the server",
        variant: "destructive",
      });
      return false;
    }
  },
};
```
