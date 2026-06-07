from contextlib import asynccontextmanager
from fastapi import FastAPI
import database
from redis_client import startup_redis, shutdown_redis
from api.books import router as book_router
from api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)
    await startup_redis()
    yield
    await shutdown_redis()


app = FastAPI(
    title="Book Catalog API",
    description="REST API with JWT authentication and Redis-based rate limiting",
    version="7.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(book_router)


@app.get("/")
async def root():
    return {"message": "Library API is running"}
