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