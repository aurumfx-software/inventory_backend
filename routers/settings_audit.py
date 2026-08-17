from fastapi import APIRouter
from db.database_store import db, save_db
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["Settings & Audit"])

@router.get("/settings")
def get_settings():
    return {"success": True, "data": db["settings"]}

@router.post("/settings")
def update_settings(payload: Dict[str, Any]):
    db["settings"].update(payload)
    save_db()
    return {"success": True, "data": db["settings"]}

@router.get("/audit-logs")
def get_audit_logs():
    return {"success": True, "data": db["audit_logs"]}

@router.get("/notifications")
def get_notifications():
    return {"success": True, "data": db["notifications"]}
