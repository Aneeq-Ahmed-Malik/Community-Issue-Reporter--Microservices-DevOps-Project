from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Notification Service", version="1.0.0")


class NotificationCreate(BaseModel):
    user_id: str
    channel: Literal["in_app", "email"] = "in_app"
    subject: str = Field(min_length=3, max_length=120)
    message: str = Field(min_length=3, max_length=1000)
    metadata: Dict[str, Any] = Field(default_factory=dict)


notifications: List[Dict[str, Any]] = []


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "notification-service"}


@app.post("/notify", status_code=201)
def create_notification(payload: NotificationCreate) -> dict:
    record = {
        "id": str(uuid4()),
        "user_id": payload.user_id,
        "channel": payload.channel,
        "subject": payload.subject,
        "message": payload.message,
        "metadata": payload.metadata,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    notifications.append(record)
    return record


@app.get("/notifications")
def list_notifications(user_id: Optional[str] = Query(default=None)) -> dict:
    items = notifications
    if user_id:
        items = [item for item in notifications if item["user_id"] == user_id]

    return {"items": items, "count": len(items)}
