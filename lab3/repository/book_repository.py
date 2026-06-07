import json
import base64
from typing import Optional
from sqlalchemy import select, delete, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.book import Book


def encode_cursor(data: dict) -> str:
    payload = json.dumps(data).encode()
    return base64.urlsafe_b64encode(payload).decode()


def decode_cursor(token: str) -> dict:
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ValueError
        return result
    except Exception:
        raise ValueError("Invalid cursor token")


async def get_page(
    db: AsyncSession,
    status: Optional[str] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = None,
    cursor: Optional[str] = None,
    limit: int = 10,
) -> tuple[list[Book], Optional[str]]:
    position = decode_cursor(cursor) if cursor else {}

    stmt = select(Book)

    if status is not None:
        stmt = stmt.where(Book.status == status)

    if author is not None:
        stmt = stmt.where(Book.author.ilike(f"%{author}%"))

    if sort_by == "title":
        if position:
            pt, pi = position.get("title", ""), position.get("id", "")
            stmt = stmt.where(or_(Book.title > pt, and_(Book.title == pt, Book.id > pi)))
        stmt = stmt.order_by(Book.title, Book.id)
    elif sort_by == "year":
        if position:
            py, pi = position.get("year", 0), position.get("id", "")
            stmt = stmt.where(or_(Book.year > py, and_(Book.year == py, Book.id > pi)))
        stmt = stmt.order_by(Book.year, Book.id)
    else:
        if position:
            stmt = stmt.where(Book.id > position.get("id", ""))
        stmt = stmt.order_by(Book.id)

    result = await db.execute(stmt.limit(limit + 1))
    entries = list(result.scalars().all())

    has_more = len(entries) > limit
    if has_more:
        entries = entries[:limit]

    next_cursor: Optional[str] = None
    if has_more and entries:
        tail = entries[-1]
        if sort_by == "title":
            next_cursor = encode_cursor({"title": tail.title, "id": tail.id})
        elif sort_by == "year":
            next_cursor = encode_cursor({"year": tail.year, "id": tail.id})
        else:
            next_cursor = encode_cursor({"id": tail.id})

    return entries, next_cursor


async def lookup_by_id(db: AsyncSession, book_id: str) -> Optional[Book]:
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()


async def add_record(db: AsyncSession, data: dict) -> Book:
    entry = Book(**data)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def delete_record(db: AsyncSession, book_id: str) -> bool:
    result = await db.execute(delete(Book).where(Book.id == book_id))
    await db.commit()
    return result.rowcount > 0
