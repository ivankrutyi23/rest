import asyncio
import os

import database
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

_TEST_DB = "test_library.db"
_test_engine = create_async_engine(f"sqlite+aiosqlite:///{_TEST_DB}")
_TestSession = async_sessionmaker(_test_engine, expire_on_commit=False)
database.engine = _test_engine

import fakeredis.aioredis
from redis_client import get_redis_client

_fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)


async def _override_redis():
    return _fake_redis


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from main import app
from database import get_db
from models.book import Book
from models.user import User
from services import auth_service


async def _override_get_db():
    async with _TestSession() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db
app.dependency_overrides[get_redis_client] = _override_redis


@pytest.fixture(scope="session", autouse=True)
def client():
    if os.path.exists(_TEST_DB):
        os.remove(_TEST_DB)
    with TestClient(app) as c:
        yield c
    if os.path.exists(_TEST_DB):
        os.remove(_TEST_DB)


@pytest.fixture(autouse=True)
def reset(client):
    yield
    asyncio.run(_purge())
    auth_service.clear_tokens()
    asyncio.run(_fake_redis.flushall())


async def _purge():
    async with _TestSession() as session:
        await session.execute(delete(Book))
        await session.execute(delete(User))
        await session.commit()


@pytest.fixture
def fake_redis():
    return _fake_redis


USER_A = {"username": "alice", "password": "alice123"}
USER_B = {"username": "bob", "password": "bob456"}
SAMPLE = {
    "title": "Kobzar", "author": "Taras Shevchenko",
    "year": 1840, "pages": 312, "status": "free",
}


def _signup_and_login(client, creds: dict) -> dict:
    client.post("/auth/register", json=creds)
    resp = client.post("/auth/login", json=creds)
    return resp.json()


@pytest.fixture
def tokens_a(client):
    return _signup_and_login(client, USER_A)


@pytest.fixture
def tokens_b(client):
    return _signup_and_login(client, USER_B)


@pytest.fixture
def headers_a(tokens_a):
    return {"Authorization": f"Bearer {tokens_a['access_token']}"}


@pytest.fixture
def headers_b(tokens_b):
    return {"Authorization": f"Bearer {tokens_b['access_token']}"}
