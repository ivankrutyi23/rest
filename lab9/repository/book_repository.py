from typing import Optional
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.book import Book


async def get_many(
    db: AsyncSession,
    status: Optional[str] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> tuple[list[Book], int]:
    stmt = select(Book)
    count_stmt = select(func.count()).select_from(Book)

    if status is not None:
        stmt = stmt.where(Book.status == status)
        count_stmt = count_stmt.where(Book.status == status)
    if author is not None:
        pattern = f"%{author}%"
        stmt = stmt.where(Book.author.ilike(pattern))
        count_stmt = count_stmt.where(Book.author.ilike(pattern))

    if sort_by == "title":
        stmt = stmt.order_by(Book.title)
    elif sort_by == "year":
        stmt = stmt.order_by(Book.year)

    rows = await db.execute(stmt.limit(limit).offset(offset))
    total_row = await db.execute(count_stmt)
    return list(rows.scalars().all()), total_row.scalar()


async def get_one(db: AsyncSession, uid: str) -> Optional[Book]:
    result = await db.execute(select(Book).where(Book.id == uid))
    return result.scalar_one_or_none()


async def store(db: AsyncSession, data: dict) -> Book:
    book = Book(**data)
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


async def remove(db: AsyncSession, uid: str) -> bool:
    result = await db.execute(delete(Book).where(Book.id == uid))
    await db.commit()
    return result.rowcount > 0
