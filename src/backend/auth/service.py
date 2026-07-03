from sqlalchemy.orm import Session
from src.backend.db.models.user import User
from src.backend.core.security import hash_password, verify_password
from src.backend.auth.tokens import create_access_token
from src.shared.utils.logging import get_logger
import uuid

logger = get_logger("auth")

def register_user(db: Session, username: str, email: str, password: str, role: str = "inspector"):
    existing = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing:
        return None, "Username or email already exists"
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"New user registered: {username}")
    return user, None

def login_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None, "User not found"
    if not verify_password(password, user.hashed_password):
        return None, "Invalid password"
    if not user.is_active:
        return None, "Account is inactive"
    token = create_access_token({"sub": user.id, "username": user.username, "role": user.role})
    logger.info(f"User logged in: {username}")
    return token, None

def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()