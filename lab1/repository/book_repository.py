from models.book import _store


async def get_all() -> list[dict]:
    return list(_store)


async def get_by_id(book_id: str) -> dict | None:
    matched = [b for b in _store if b["id"] == book_id]
    return matched[0] if matched else None


async def save(entry: dict) -> dict:
    _store.append(entry)
    return entry


async def delete(book_id: str) -> bool:
    for idx, book in enumerate(_store):
        if book["id"] == book_id:
            _store.pop(idx)
            return True
    return False
