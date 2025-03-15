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