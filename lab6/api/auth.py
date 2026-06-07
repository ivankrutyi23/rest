from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import Credentials, UserView
from schemas.token import LoginRequest, TokenResponse, RefreshRequest
from services import auth_service
from database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserView, status_code=201)
async def register(payload: Credentials, db: AsyncSession = Depends(get_db)):
    user = await auth_service.create_account(db, payload)
    if user is None:
        raise HTTPException(status_code=409, detail="Username already taken")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    tokens = await auth_service.authenticate(db, payload.username, payload.password)
    if tokens is None:
        raise HTTPException(status_code=401, detail="Wrong username or password")
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    tokens = await auth_service.rotate(db, payload.refresh_token)
    if tokens is None:
        raise HTTPException(status_code=401, detail="Token is invalid or has expired")
    return tokens


@router.post("/logout")
async def logout(payload: RefreshRequest):
    auth_service.sign_out(payload.refresh_token)
    return {"message": "Logged out"}
