from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.book import NewBook, BookRecord, Availability, CursorPage
from services import book_service
from database import get_db

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=CursorPage)
async def get_books(
    status: Optional[Availability] = Query(default=None, description="Filter by availability"),
    author: Optional[str] = Query(default=None, description="Author search (partial, case-insensitive)"),
    sort_by: Optional[str] = Query(default=None, pattern="^(title|year)$"),
    cursor: Optional[str] = Query(default=None, description="Cursor token from previous page response"),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    try:
        books, next_cursor = await book_service.list_books(
            db, status=status, author=author, sort_by=sort_by, cursor=cursor, limit=limit
        )
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid cursor format")
    return CursorPage(items=books, next_cursor=next_cursor, limit=limit)


@router.get("/{book_id}", response_model=BookRecord)
async def get_book(book_id: str, db: AsyncSession = Depends(get_db)):
    book = await book_service.one_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookRecord, status_code=201)
async def create_book(payload: NewBook, db: AsyncSession = Depends(get_db)):
    return await book_service.make_book(db, payload)


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str, db: AsyncSession = Depends(get_db)):
    await book_service.drop_book(db, book_id)
