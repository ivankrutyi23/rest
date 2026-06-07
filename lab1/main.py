from fastapi import FastAPI
from api.books import router as book_router

app = FastAPI(
    title="Book Catalog API",
    description="Simple REST API for managing a book catalog",
    version="0.1.0",
)

app.include_router(book_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Library API is running"}
