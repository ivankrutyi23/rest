from contextlib import asynccontextmanager
from fastapi import FastAPI
import database
from api.books import router as book_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect_db()
    yield
    await database.close_db()


app = FastAPI(
    title="Book Catalog API",
    description="REST API for book catalog management with MongoDB",
    version="4.0.0",
    lifespan=lifespan,
)

app.include_router(book_router)


@app.get("/")
async def root():
    return {"message": "Library API is running"}
