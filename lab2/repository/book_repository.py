from typing import Optional
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.book import Book


async def query_books(
    db: AsyncSession,
    status: Optional[str] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> tuple[list[Book], int]:
    base_q = select(Book)
    count_q = select(func.count()).select_from(Book)

    if status is not None:
        base_q = base_q.where(Book.status == status)
        count_q = count_q.where(Book.status == status)

    if author is not None:
        pattern = f"%{author}%"
        base_q = base_q.where(Book.author.ilike(pattern))
        count_q = count_q.where(Book.author.ilike(pattern))

    if sort_by == "title":
        base_q = base_q.order_by(Book.title)
    elif sort_by == "year":
        base_q = base_q.order_by(Book.year)

    base_q = base_q.limit(limit).offset(offset)

    rows = await db.execute(base_q)
    count_row = await db.execute(count_q)

    return list(rows.scalars().all()), count_row.scalar()


async def fetch_by_id(db: AsyncSession, book_id: str) -> Optional[Book]:
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()


async def persist(db: AsyncSession, data: dict) -> Book:
    book = Book(**data)
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


async def erase(db: AsyncSession, book_id: str) -> bool:
    result = await db.execute(delete(Book).where(Book.id == book_id))
    await db.commit()
    return result.rowcount > 0
