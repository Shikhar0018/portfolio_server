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