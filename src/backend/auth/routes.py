from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from src.backend.db.session import get_db
from src.backend.auth import service
from src.backend.auth.tokens import decode_access_token
from src.shared.utils.logging import get_logger

logger = get_logger("auth")
router = APIRouter(prefix="/api/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "inspector"

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user, error = service.register_user(
        db, request.username, request.email,
        request.password, request.role
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token, error = service.login_user(db, form_data.username, form_data.password)
    if error:
        raise HTTPException(status_code=401, detail=error)
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = service.get_user_by_id(db, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }