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