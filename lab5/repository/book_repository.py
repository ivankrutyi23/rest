from typing import Optional
from models.book import _store


def get_catalog(
    status: Optional[str] = None,
    author: Optional[str] = None,
    pages_min: Optional[int] = None,
    sort_by: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> tuple[list[dict], int]:
    items = list(_store)

    if status is not None:
        items = [b for b in items if b["status"] == status]
    if author is not None:
        needle = author.lower()
        items = [b for b in items if needle in b["author"].lower()]
    if pages_min is not None:
        items = [b for b in items if b.get("pages") and b["pages"] >= pages_min]

    if sort_by == "title":
        items.sort(key=lambda b: b["title"].lower())
    elif sort_by == "year":
        items.sort(key=lambda b: b["year"])

    return items[offset: offset + limit], len(items)


def get_by_id(uid: str) -> Optional[dict]:
    return next((b for b in _store if b["id"] == uid), None)


def save_entry(entry: dict) -> dict:
    _store.append(entry)
    return entry


def delete_entry(uid: str) -> bool:
    for idx, b in enumerate(_store):
        if b["id"] == uid:
            _store.pop(idx)
            return True
    return False
