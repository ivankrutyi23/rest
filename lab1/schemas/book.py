from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Availability(str, Enum):
    AVAILABLE = "available"
    ISSUED = "issued"


class NewBook(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    year: int = Field(..., ge=1000, le=2100)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Availability = Field(default=Availability.AVAILABLE)


class BookRecord(BaseModel):
    id: str
    title: str
    author: str
    year: int
    description: Optional[str] = None
    status: Availability
