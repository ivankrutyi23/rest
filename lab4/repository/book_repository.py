import uuid
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.book import BOOKS_COLLECTION


def _doc_to_dict(doc: dict) -> dict:
    entry = dict(doc)
    entry["id"] = str(entry.pop("_id"))
    return entry


async def fetch_all(
    db: AsyncIOMotorDatabase,
    status: Optional[str] = None,
    author: Optional[str] = None,
    pages_min: Optional[int] = None,
    sort_by: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> tuple[list[dict], int]:
    filters: dict = {}
    if status is not None:
        filters["status"] = status
    if author is not None:
        filters["author"] = {"$regex": author, "$options": "i"}
    if pages_min is not None:
        filters["pages"] = {"$gte": pages_min}

    sort_spec = [("_id", 1)]
    if sort_by == "title":
        sort_spec = [("title", 1), ("_id", 1)]
    elif sort_by == "year":
        sort_spec = [("year", 1), ("_id", 1)]

    col = db[BOOKS_COLLECTION]
    count = await col.count_documents(filters)
    raw = await col.find(filters).sort(sort_spec).skip(offset).limit(limit).to_list(length=limit)
    return [_doc_to_dict(d) for d in raw], count


async def find_one(db: AsyncIOMotorDatabase, uid: str) -> Optional[dict]:
    doc = await db[BOOKS_COLLECTION].find_one({"_id": uid})
    return _doc_to_dict(doc) if doc else None


async def store(db: AsyncIOMotorDatabase, data: dict) -> dict:
    new_id = str(uuid.uuid4())
    await db[BOOKS_COLLECTION].insert_one({"_id": new_id, **data})
    return {"id": new_id, **data}


async def discard(db: AsyncIOMotorDatabase, uid: str) -> bool:
    result = await db[BOOKS_COLLECTION].delete_one({"_id": uid})
    return result.deleted_count > 0
