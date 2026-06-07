from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class Availability(str, Enum):
    FREE = "free"
    ON_LOAN = "on_loan"


class NewBook(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    year: int = Field(..., ge=1000, le=2100)
    pages: Optional[int] = Field(None, ge=1, le=10000)
    summary: Optional[str] = Field(None, max_length=1000)
    status: Availability = Availability.FREE


class BookRecord(BaseModel):
    id: str
    title: str
    author: str
    year: int
    pages: Optional[int] = None
    summary: Optional[str] = None
    status: Availability

    model_config = {"from_attributes": True}


class PagedBooks(BaseModel):
    items: List[BookRecord]
    total: int
    limit: int
    offset: int
