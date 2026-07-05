"""
Seed demo users into the database.
Run once: python scripts/seed_users.py
"""

import sys
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backend.db.session import SessionLocal
from src.backend.db.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEMO_USERS = [
    {
        "username": "arjun.mehta",
        "email": "inspector@aeroinspect.io",
        "password": "demo1234",
        "role": "inspector",
    },
    {
        "username": "priya.nair",
        "email": "engineer@aeroinspect.io",
        "password": "demo1234",
        "role": "engineer",
    },
    {
        "username": "rohan.desai",
        "email": "admin@aeroinspect.io",
        "password": "demo1234",
        "role": "admin",
    },
]


def seed():
    db = SessionLocal()

    for user_data in DEMO_USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            print(f"User already exists: {user_data['email']}")
            continue

        user = User(
            id=str(uuid.uuid4()),
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=pwd_context.hash(user_data["password"]),
            role=user_data["role"],
            is_active=True,
        )
        db.add(user)
        print(f"Added user: {user_data['email']} ({user_data['role']})")

    db.commit()
    db.close()
    print("Seeding complete.")


if __name__ == "__main__":
    seed()