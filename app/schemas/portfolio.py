from typing import List, Optional
from pydantic import BaseModel

class PortfolioBase(BaseModel):
    title: str
    description: str
    image: str
    url: str
    tags: List[str]
    color: str
    experiences: List[str]
    projects: List[str]


class Portfolio(PortfolioBase):
    id: str

    class Config:
        orm_mode = True

