from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.book import NewBook, BookRecord, Availability, PagedBooks
from services import book_service
from database import get_db
from core.dependencies import current_user, maybe_user

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=PagedBooks)
async def list_books(
    status: Optional[Availability] = Query(default=None),
    author: Optional[str] = Query(default=None),
    pages_min: Optional[int] = Query(default=None, ge=1),
    sort_by: Optional[str] = Query(default=None, pattern="^(title|year)$"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    records, total = await book_service.list_books(
        db, status=status, author=author, pages_min=pages_min,
        sort_by=sort_by, limit=limit, offset=offset,
    )
    return PagedBooks(items=records, total=total, limit=limit, offset=offset)


@router.get("/{uid}", response_model=BookRecord)
async def get_book(uid: str, db: AsyncSession = Depends(get_db)):
    book = await book_service.one_book(db, uid)
    if book is None:
        raise HTTPException(status_code=404, detail="Not found")
    return book


@router.post("/", response_model=BookRecord, status_code=201)
async def add_book(
    payload: NewBook,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(current_user),
):
    return await book_service.make_book(db, payload)


@router.delete("/{uid}", status_code=204)
async def delete_book(
    uid: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(current_user),
):
    await book_service.drop_book(db, uid)
