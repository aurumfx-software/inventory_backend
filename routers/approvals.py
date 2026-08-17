from fastapi import APIRouter
from db.database_store import db, save_db
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])

class ApprovalAction(BaseModel):
    approval_id: str
    action: str  # 'Approve' | 'Reject'
    comments: Optional[str] = ""

@router.get("")
@router.get("/requests")
def get_approval_requests():
    return {"success": True, "data": db["approval_requests"]}

@router.get("/history")
def get_approval_history():
    return {"success": True, "data": [a for a in db["approval_requests"] if a.get("status") in ["Approved", "Rejected"]]}

@router.get("/workflows")
def get_approval_workflows():
    return {"success": True, "data": db["approval_workflows"]}

@router.get("/delegations")
def get_approval_delegations():
    if "approval_delegations" not in db:
        db["approval_delegations"] = []
    return {"success": True, "data": db["approval_delegations"]}

@router.post("/delegations")
def create_approval_delegation(payload: Dict[str, Any]):
    if "approval_delegations" not in db:
        db["approval_delegations"] = []
    
    new_del = {
        "id": f"del-{len(db['approval_delegations']) + 1}",
        "from_user": payload.get("from_user", "usr-04"),
        "to_user": payload.get("to_user", "usr-02"),
        "start_date": payload.get("start_date", "2026-08-17"),
        "end_date": payload.get("end_date", "2026-08-31"),
        "reason": payload.get("reason", "Annual Leave Delegation"),
        "status": "Active"
    }
    db["approval_delegations"].append(new_del)
    save_db()
    return {"success": True, "data": new_del, "message": "Approval delegation rule saved successfully."}

@router.post("/action")
@router.post("/{approval_id}/action")
def take_approval_action(req: ApprovalAction, approval_id: Optional[str] = None):
    app_id = req.approval_id or approval_id
    app_req = next((a for a in db["approval_requests"] if a["id"] == app_id), None)
    if app_req:
        app_req["status"] = "Approved" if req.action == "Approve" else "Rejected"
        app_req["comments"] = req.comments or ""

        if app_req.get("transaction_type") == "INDENT":
            ind = next((i for i in db["indents"] if i["id"] == app_req.get("transaction_id")), None)
            if ind:
                ind["status"] = "Approved" if req.action == "Approve" else "Rejected"

        save_db()
        return {"success": True, "message": f"Transaction {req.action}d successfully"}
    return {"success": False, "message": "Approval request not found"}
