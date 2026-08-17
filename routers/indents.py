from fastapi import APIRouter
from db.database_store import db, save_db, get_next_doc_number
from schemas.schemas import IndentCreate
from datetime import datetime

router = APIRouter(prefix="/api/indents", tags=["Indents"])

@router.get("")
def get_indents():
    return {"success": True, "data": db["indents"]}

@router.post("")
def create_indent(req: IndentCreate):
    indent_num = get_next_doc_number("IND")
    new_id = f"ind-{len(db['indents']) + 1002}"
    now = datetime.now().isoformat()

    new_indent = {
        "id": new_id,
        "indent_number": indent_num,
        "request_date": datetime.now().strftime("%Y-%m-%d"),
        "department_id": req.department_id or "dept-01",
        "requested_by": "usr-05",
        "required_date": req.required_date or "2026-08-30",
        "purpose": req.purpose,
        "priority": req.priority or "Medium",
        "cost_centre": req.cost_centre or "IT-001",
        "remarks": req.remarks or "",
        "status": "Submitted",
        "total_estimated_amount": 150000,
        "created_at": now
    }
    
    db["indents"].append(new_indent)

    approval = {
        "id": f"app-{len(db['approval_requests']) + 1}",
        "transaction_type": "INDENT",
        "transaction_id": new_id,
        "approval_level": 1,
        "approver_id": "usr-04",
        "assigned_date": now,
        "status": "Pending",
        "comments": ""
    }
    db["approval_requests"].append(approval)

    db["audit_logs"].append({
        "id": f"aud-{len(db['audit_logs']) + 1}",
        "user_id": "usr-05",
        "action": "CREATE_INDENT",
        "module": "PROCUREMENT",
        "record_id": new_id,
        "details": f"Created Indent Requisition {indent_num}",
        "timestamp": now,
        "ip_address": "127.0.0.1"
    })

    save_db()
    return {"success": True, "data": new_indent}

@router.get("/{indent_id}")
def get_indent(indent_id: str):
    indent = next((i for i in db["indents"] if i["id"] == indent_id), None)
    if indent:
        return {"success": True, "data": indent}
    return {"success": False, "message": "Indent not found"}

@router.post("/{indent_id}/submit")
def submit_indent(indent_id: str):
    indent = next((i for i in db["indents"] if i["id"] == indent_id), None)
    if indent:
        indent["status"] = "Submitted"
        save_db()
        return {"success": True, "data": indent}
    return {"success": False, "message": "Indent not found"}

@router.post("/{indent_id}/cancel")
def cancel_indent(indent_id: str):
    indent = next((i for i in db["indents"] if i["id"] == indent_id), None)
    if indent:
        indent["status"] = "Cancelled"
        save_db()
        return {"success": True, "data": indent}
    return {"success": False, "message": "Indent not found"}

@router.delete("/{indent_id}")
def delete_indent(indent_id: str):
    global db
    db["indents"] = [i for i in db["indents"] if i["id"] != indent_id]
    save_db()
    return {"success": True, "message": "Indent deleted successfully"}
