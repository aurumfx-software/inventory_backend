from fastapi import APIRouter, Request, Header
from db.database_store import db, save_db, filter_by_company
from typing import Dict, Any
from datetime import datetime

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
def get_audit_logs(request: Request, x_company_name: str = Header(None)):
    co = x_company_name or request.headers.get("x-company-name") or request.query_params.get("company_name")
    data = filter_by_company(db.get("audit_logs", []), co)
    return {"success": True, "data": data}

@router.post("/audit-logs")
def create_audit_log(payload: Dict[str, Any]):
    new_log = {
        "id": f"aud-{len(db['audit_logs']) + 1}",
        "timestamp": datetime.now().isoformat(),
        "user_name": payload.get("user_name", "Current Logged-in User"),
        "action": payload.get("action", "USER_ACTION"),
        "category": payload.get("category", "General"),
        "module": payload.get("module", "System"),
        "record_id": payload.get("record_id", "N/A"),
        "ip_address": "127.0.0.1",
        "details": payload.get("details", "")
    }
    db["audit_logs"].append(new_log)
    save_db()
    return {"success": True, "data": new_log}

@router.get("/notifications")
def get_notifications():
    return {"success": True, "data": db["notifications"]}

@router.post("/notifications/{notif_id}/read")
def mark_notification_read(notif_id: str):
    for n in db["notifications"]:
        if n.get("id") == notif_id:
            n["is_read"] = True
            save_db()
            return {"success": True, "data": n}
    return {"success": True, "message": "Notification marked read"}

@router.post("/import/{import_type}")
def handle_bulk_import(import_type: str, payload: Dict[str, Any]):
    rows = payload.get("rows", [])
    return {"success": True, "message": f"Successfully processed {len(rows)} bulk import rows for {import_type}."}

@router.get("/attachments")
def get_attachments():
    if "attachments" not in db:
        db["attachments"] = [
            { "id": "att-01", "module": "Purchase Order", "name": "PO_Vendor_Quote_Approved.pdf", "fileType": "PDF", "size": "1.2 MB", "storageUrl": "local://storage/docs/PO_8801.pdf", "uploadedBy": "Rajesh Kumar", "date": "2026-08-09" }
        ]
    return {"success": True, "data": db["attachments"]}

@router.post("/attachments")
def create_attachment(payload: Dict[str, Any]):
    if "attachments" not in db:
        db["attachments"] = []
    new_att = {
        "id": f"att-{len(db['attachments']) + 1}",
        "module": payload.get("module", "Indents"),
        "name": payload.get("name", "Document.pdf"),
        "fileType": "PDF",
        "size": "1.2 MB",
        "storageUrl": f"local://storage/docs/{payload.get('name')}",
        "uploadedBy": "Sarah Jenkins",
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    db["attachments"].append(new_att)
    save_db()
    return {"success": True, "data": new_att}

@router.post("/purge-sample-data")
def trigger_purge_sample_data():
    from db.database_store import purge_all_sample_data
    purge_all_sample_data()
    return {"success": True, "message": "All sample demo data permanently purged."}
