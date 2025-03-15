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