from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional
from uuid import uuid4
import os

from fastapi import FastAPI, HTTPException, Query
import httpx
from pydantic import BaseModel, Field

app = FastAPI(title="Issue Service", version="1.0.0")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://auth-service:8000")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "3"))


class IssueCreate(BaseModel):
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=10, max_length=1200)
    reporter_id: str


class IssueStatusUpdate(BaseModel):
    status: Literal["open", "in_progress", "resolved"]
    updated_by: str


class CommentCreate(BaseModel):
    user_id: str
    text: str = Field(min_length=1, max_length=500)


class Issue(BaseModel):
    id: str
    title: str
    description: str
    reporter_id: str
    status: Literal["open", "in_progress", "resolved"]
    comments: List[dict]
    created_at: str
    updated_at: str


issues_by_id: Dict[str, Dict] = {}


async def _ensure_user_exists(user_id: str) -> None:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        try:
            response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=503, detail="User service unavailable") from exc

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")
    if response.status_code >= 500:
        raise HTTPException(status_code=503, detail="User service error")


async def _send_notification(user_id: str, subject: str, message: str, metadata: Optional[dict] = None) -> None:
    payload = {
        "user_id": user_id,
        "channel": "in_app",
        "subject": subject,
        "message": message,
        "metadata": metadata or {},
    }

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        try:
            await client.post(f"{NOTIFICATION_SERVICE_URL}/notify", json=payload)
        except httpx.HTTPError:
            # Notification failures should not block the issue workflow.
            return


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "issue-service"}


@app.post("/issues", response_model=Issue, status_code=201)
async def create_issue(payload: IssueCreate) -> Issue:
    await _ensure_user_exists(payload.reporter_id)

    issue_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    issue = {
        "id": issue_id,
        "title": payload.title,
        "description": payload.description,
        "reporter_id": payload.reporter_id,
        "status": "open",
        "comments": [],
        "created_at": now,
        "updated_at": now,
    }
    issues_by_id[issue_id] = issue

    await _send_notification(
        user_id=payload.reporter_id,
        subject="Issue created",
        message=f"Your issue '{payload.title}' has been created with status open.",
        metadata={"issue_id": issue_id, "status": "open"},
    )

    return Issue(**issue)


@app.get("/issues")
def list_issues(status: Optional[str] = Query(default=None)) -> dict:
    items = list(issues_by_id.values())
    if status:
        items = [item for item in items if item["status"] == status]

    return {"items": items, "count": len(items)}


@app.get("/issues/{issue_id}", response_model=Issue)
def get_issue(issue_id: str) -> Issue:
    issue = issues_by_id.get(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    return Issue(**issue)


@app.patch("/issues/{issue_id}/status", response_model=Issue)
async def update_issue_status(issue_id: str, payload: IssueStatusUpdate) -> Issue:
    issue = issues_by_id.get(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    await _ensure_user_exists(payload.updated_by)

    issue["status"] = payload.status
    issue["updated_at"] = datetime.now(timezone.utc).isoformat()

    await _send_notification(
        user_id=issue["reporter_id"],
        subject="Issue status updated",
        message=f"Issue '{issue['title']}' is now '{payload.status}'.",
        metadata={"issue_id": issue_id, "status": payload.status},
    )

    return Issue(**issue)


@app.post("/issues/{issue_id}/comments", response_model=Issue)
async def add_comment(issue_id: str, payload: CommentCreate) -> Issue:
    issue = issues_by_id.get(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    await _ensure_user_exists(payload.user_id)

    issue["comments"].append(
        {
            "id": str(uuid4()),
            "user_id": payload.user_id,
            "text": payload.text,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    issue["updated_at"] = datetime.now(timezone.utc).isoformat()

    return Issue(**issue)
