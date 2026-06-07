import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 45
REFRESH_EXPIRE_DAYS = 14


def make_hash(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def validate_hash(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def issue_access(user_id: str, username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    payload = {
        "uid": user_id,
        "username": username,
        "kind": "access",
        "jti": str(uuid.uuid4()),
        "exp": expires_at,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def issue_refresh(user_id: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRE_DAYS)
    payload = {
        "uid": user_id,
        "kind": "refresh",
        "jti": str(uuid.uuid4()),
        "exp": expires_at,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def read_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
