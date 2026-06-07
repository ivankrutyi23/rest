from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError

from core.security import read_token

_bearer = HTTPBearer(auto_error=False)


def maybe_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[dict]:
    if credentials is None:
        return None
    try:
        payload = read_token(credentials.credentials)
        if payload.get("kind") != "access":
            return None
        return {"id": payload["uid"], "username": payload["username"]}
    except InvalidTokenError:
        return None


def current_user(user: Optional[dict] = Depends(maybe_user)) -> dict:
    if user is None:
        raise HTTPException(status_code=401, detail="Authorization required")
    return user
