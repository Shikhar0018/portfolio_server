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