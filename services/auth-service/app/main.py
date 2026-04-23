from datetime import datetime, timezone
import hashlib
from typing import Dict
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="Auth Service", version="1.0.0")


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr
    created_at: str


users_by_id: Dict[str, Dict[str, str]] = {}
users_by_username: Dict[str, str] = {}


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "auth-service"}


@app.post("/users/register", response_model=UserPublic, status_code=201)
def register(payload: UserRegister) -> UserPublic:
    username_key = payload.username.strip().lower()
    if username_key in users_by_username:
        raise HTTPException(status_code=409, detail="Username already exists")

    user_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    users_by_id[user_id] = {
        "id": user_id,
        "username": payload.username.strip(),
        "email": payload.email,
        "password_hash": _hash_password(payload.password),
        "created_at": now,
    }
    users_by_username[username_key] = user_id

    return UserPublic(
        id=user_id,
        username=users_by_id[user_id]["username"],
        email=users_by_id[user_id]["email"],
        created_at=users_by_id[user_id]["created_at"],
    )


@app.post("/users/login")
def login(payload: UserLogin) -> dict:
    username_key = payload.username.strip().lower()
    user_id = users_by_username.get(username_key)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_record = users_by_id[user_id]
    if user_record["password_hash"] != _hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": f"user-{user_record['id']}",
        "token_type": "bearer",
        "user_id": user_record["id"],
    }


@app.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: str) -> UserPublic:
    user_record = users_by_id.get(user_id)
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPublic(
        id=user_record["id"],
        username=user_record["username"],
        email=user_record["email"],
        created_at=user_record["created_at"],
    )


@app.get("/users")
def list_users() -> dict:
    return {
        "items": [
            {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "created_at": user["created_at"],
            }
            for user in users_by_id.values()
        ],
        "count": len(users_by_id),
    }
