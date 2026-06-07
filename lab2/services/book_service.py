import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.book import NewBook, Availability
from repository import book_repository
from models.book import Book


async def list_books(
    db: AsyncSession,
    status: Optional[Availability] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> tuple[list[Book], int]:
    status_val = status.value if status is not None else None
    return await book_repository.query_books(
        db,
        status=status_val,
        author=author,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )


async def one_book(db: AsyncSession, book_id: str) -> Optional[Book]:
    return await book_repository.fetch_by_id(db, book_id)


async def make_book(db: AsyncSession, payload: NewBook) -> Book:
    data = {
        "id": str(uuid.uuid4()),
        "title": payload.title,
        "author": payload.author,
        "year": payload.year,
        "description": payload.description,
        "status": payload.status.value,
    }
    return await book_repository.persist(db, data)


async def drop_book(db: AsyncSession, book_id: str) -> bool:
    return await book_repository.erase(db, book_id)
