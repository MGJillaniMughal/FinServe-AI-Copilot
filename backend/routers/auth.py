"""Authentication endpoints."""
from fastapi import APIRouter, HTTPException, status
from backend.config import settings
from backend.models import LoginRequest, TokenResponse
from backend import database as db
from backend.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = db.get_user(payload.email.lower().strip())
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    token = create_access_token(user["email"], user["name"], user["role"])
    return TokenResponse(
        access_token=token, name=user["name"], role=user["role"],
        expires_in=settings.TOKEN_EXPIRE_MINUTES * 60,
    )
