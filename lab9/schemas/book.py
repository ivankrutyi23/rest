from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Availability(str, Enum):
    FREE = "free"
    ON_LOAN = "on_loan"


class NewBook(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    year: int = Field(..., ge=1000, le=2100)
    status: Availability = Field(default=Availability.FREE)
    pages: Optional[int] = Field(default=None, ge=1, le=10000)
    summary: Optional[str] = Field(default=None, max_length=1000)


class BookRecord(BaseModel):
    id: str
    title: str
    author: str
    year: int
    status: Availability
    pages: Optional[int] = None
    summary: Optional[str] = None

    model_config = {"from_attributes": True}


class PagedBooks(BaseModel):
    items: list[BookRecord]
    total: int
    limit: int
    offset: int
