import time
import uuid
from typing import Optional

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Request

from core.dependencies import maybe_user
from redis_client import get_redis_client

_LIMITS = {
    "anonymous": (3, 60),
    "authenticated": (15, 60),
}


async def enforce_limit(
    request: Request,
    user: Optional[dict] = Depends(maybe_user),
    redis: aioredis.Redis = Depends(get_redis_client),
) -> None:
    user_id = user["id"] if user else None
    identity = user_id or request.client.host
    tier = "authenticated" if user_id else "anonymous"
    cap, window = _LIMITS[tier]

    key = f"rl:{identity}"
    now = int(time.time())
    cutoff = now - window

    await redis.zremrangebyscore(key, 0, cutoff)
    current_count = await redis.zcard(key)

    if current_count >= cap:
        wait = window - (now - cutoff)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {wait} seconds.",
            headers={"Retry-After": str(wait)},
        )

    await redis.zadd(key, {f"{now}:{uuid.uuid4()}": now})
    await redis.expire(key, window)
