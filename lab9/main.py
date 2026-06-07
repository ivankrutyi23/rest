from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
from sqlalchemy import func, select

import database
from api.books import router as book_router
from models.book import Book

_CATALOG_TITLES = [
    "Kobzar", "Eneyida", "Lisova pisnia", "Tini zabutykh predkiv",
    "Intermezzo", "Zemlia", "Pryimachka", "Bur'yan", "Vovchykha",
    "Kaidasheva simia", "Chorna Rada", "Fata Morgana",
]
_CATALOG_AUTHORS = [
    "Taras Shevchenko", "Ivan Kotlyarevsky", "Lesia Ukrainka",
    "Mykhailo Kotsiubynsky", "Ivan Nechui-Levytsky", "Panas Myrny",
    "Panteleimon Kulish", "Olha Kobylianska",
]
_PAGE_COUNTS = [120, 200, 312, 440, 88, 256, 180, 350, 95, 280, 165, 420]


async def _populate_catalog() -> None:
    async with database.AsyncSessionLocal() as session:
        existing = (await session.execute(
            select(func.count()).select_from(Book)
        )).scalar()
        if existing > 0:
            return
        books = [
            Book(
                id=str(uuid4()),
                title=f"{_CATALOG_TITLES[i % len(_CATALOG_TITLES)]} {i + 1}",
                author=_CATALOG_AUTHORS[i % len(_CATALOG_AUTHORS)],
                year=1800 + (i % 200),
                pages=_PAGE_COUNTS[i % len(_PAGE_COUNTS)],
                summary=f"Entry #{i + 1}",
                status="free" if i % 4 != 0 else "on_loan",
            )
            for i in range(200)
        ]
        session.add_all(books)
        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)
    await _populate_catalog()
    yield


app = FastAPI(
    title="Book Catalog API — Load Test",
    description="FastAPI service instrumented for Locust load testing",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(book_router)


@app.get("/")
async def index():
    return {"message": "Book Catalog API"}
