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
    cursor: Optional[str] = None,
    limit: int = 10,
) -> tuple[list[Book], Optional[str]]:
    return await book_repository.get_page(
        db,
        status=status.value if status is not None else None,
        author=author,
        sort_by=sort_by,
        cursor=cursor,
        limit=limit,
    )


async def one_book(db: AsyncSession, book_id: str) -> Optional[Book]:
    return await book_repository.lookup_by_id(db, book_id)


async def make_book(db: AsyncSession, payload: NewBook) -> Book:
    data = {
        "id": str(uuid.uuid4()),
        "title": payload.title,
        "author": payload.author,
        "year": payload.year,
        "description": payload.description,
        "status": payload.status.value,
    }
    return await book_repository.add_record(db, data)


async def drop_book(db: AsyncSession, book_id: str) -> bool:
    return await book_repository.delete_record(db, book_id)
