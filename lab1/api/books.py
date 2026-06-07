from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from schemas.book import NewBook, BookRecord, Availability
from services import book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[BookRecord])
async def get_books(
    status: Optional[Availability] = Query(default=None, description="Filter by availability status"),
    author: Optional[str] = Query(default=None, description="Partial, case-insensitive author search"),
    sort_by: Optional[str] = Query(default=None, pattern="^(title|year)$"),
):
    return await book_service.list_books(status=status, author=author, sort_by=sort_by)


@router.get("/{book_id}", response_model=BookRecord)
async def get_book(book_id: str):
    book = await book_service.one_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookRecord, status_code=201)
async def create_book(payload: NewBook):
    return await book_service.make_book(payload)


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str):
    removed = await book_service.drop_book(book_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Not found")
