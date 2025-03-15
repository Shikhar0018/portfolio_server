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