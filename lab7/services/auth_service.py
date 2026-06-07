import uuid
from typing import Optional

from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import make_hash, validate_hash, issue_access, issue_refresh, read_token
from repository import user_repository
from schemas.user import Credentials

_active_refresh_tokens: set[str] = set()


async def create_account(db: AsyncSession, data: Credentials) -> Optional[object]:
    found = await user_repository.lookup_by_name(db, data.username)
    if found is not None:
        return None
    return await user_repository.add_user(db, {
        "id": str(uuid.uuid4()),
        "username": data.username,
        "hashed_password": make_hash(data.password),
        "is_active": True,
    })


async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[dict]:
    user = await user_repository.lookup_by_name(db, username)
    if not user or not validate_hash(password, user.hashed_password) or not user.is_active:
        return None
    access = issue_access(user.id, user.username)
    refresh = issue_refresh(user.id)
    _active_refresh_tokens.add(refresh)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


async def rotate(db: AsyncSession, token: str) -> Optional[dict]:
    if token not in _active_refresh_tokens:
        return None
    try:
        payload = read_token(token)
        if payload.get("kind") != "refresh":
            return None
        user_id = payload["uid"]
    except InvalidTokenError:
        _active_refresh_tokens.discard(token)
        return None

    user = await user_repository.lookup_by_id(db, user_id)
    if not user or not user.is_active:
        _active_refresh_tokens.discard(token)
        return None

    _active_refresh_tokens.discard(token)
    new_access = issue_access(user.id, user.username)
    new_refresh = issue_refresh(user.id)
    _active_refresh_tokens.add(new_refresh)
    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}


def sign_out(token: str) -> None:
    _active_refresh_tokens.discard(token)


def clear_tokens() -> None:
    _active_refresh_tokens.clear()
