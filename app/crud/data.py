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