import uuid
from typing import Optional
from schemas.book import NewBook, Availability
from repository import book_repository


async def list_books(
    status: Optional[Availability] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = None,
) -> list[dict]:
    catalog = await book_repository.get_all()

    if status is not None:
        catalog = [b for b in catalog if b["status"] == status.value]

    if author is not None:
        query = author.lower()
        catalog = [b for b in catalog if query in b["author"].lower()]

    sort_keys = {"title": lambda b: b["title"].lower(), "year": lambda b: b["year"]}
    if sort_by in sort_keys:
        catalog = sorted(catalog, key=sort_keys[sort_by])

    return catalog


async def one_book(book_id: str) -> dict | None:
    return await book_repository.get_by_id(book_id)


async def make_book(payload: NewBook) -> dict:
    entry = {"id": str(uuid.uuid4()), **payload.model_dump()}
    return await book_repository.save(entry)


async def drop_book(book_id: str) -> bool:
    return await book_repository.delete(book_id)
