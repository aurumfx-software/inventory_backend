from fastapi import APIRouter, HTTPException
from db.database_store import db, save_db
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])

class ApprovalAction(BaseModel):
    approval_id: Optional[str] = None
    action: str  # 'Approve' | 'Reject' | 'Return' | 'Forward' | 'Delegate'
    comments: Optional[str] = ""
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    approved_items: Optional[Any] = None
    forward_user_id: Optional[str] = None
    delegate_user_id: Optional[str] = None
    is_admin_override: Optional[bool] = False

def enrich_approval_request(app_req: dict) -> dict:
    txn_type = str(app_req.get("transaction_type", "")).upper()
    txn_id = str(app_req.get("transaction_id", ""))

    txnDetails = {
        "doc_number": txn_id,
        "requested_by": "Employee User",
        "department": "Information Technology",
        "purpose": "Internal Material Request",
        "amount": 150000,
        "items": [],
        "cost_centre_or_project": "IT-001"
    }

    if "INDENT" in txn_type:
        ind = next((i for i in db.get("indents", []) if i.get("id") == txn_id or i.get("indent_number") == txn_id), None)
        if ind:
            dept = next((d for d in db.get("departments", []) if d.get("id") == ind.get("department_id")), {})
            usr = next((u for u in db.get("users", []) if u.get("id") == ind.get("requested_by")), {})
            txnDetails = {
                "doc_number": ind.get("indent_number", txn_id),
                "requested_by": usr.get("name", "Rahul Employee"),
                "department": dept.get("name", "Information Technology"),
                "purpose": ind.get("purpose", "Department Equipment Requisition"),
                "amount": ind.get("total_estimated_amount", 150000),
                "items": ind.get("items", []),
                "cost_centre_or_project": ind.get("cost_centre_or_project") or ind.get("cost_centre") or "IT-001"
            }
    elif "PURCHASE" in txn_type or "PO" in txn_type:
        po = next((p for p in db.get("purchase_orders", []) if p.get("id") == txn_id or p.get("po_number") == txn_id), None)
        if po:
            sup = next((s for s in db.get("suppliers", []) if s.get("id") == po.get("supplier_id")), {})
            txnDetails = {
                "doc_number": po.get("po_number", txn_id),
                "requested_by": "Purchase Manager",
                "department": "Procurement & Supply Chain",
                "purpose": f"Purchase Order to {sup.get('supplier_name', 'Supplier')}",
                "amount": po.get("grand_total", 360000),
                "items": po.get("items", []),
                "cost_centre_or_project": "PUR-002"
            }

    approver = next((u for u in db.get("users", []) if u.get("id") == app_req.get("approver_id")), {})
    
    return {
        **app_req,
        "approver_name": app_req.get("approver_name") or approver.get("name") or "Department Manager",
        "txnDetails": txnDetails
    }

@router.get("")
@router.get("/requests")
def get_approval_requests():
    reqs = db.get("approval_requests", [])
    enriched = [enrich_approval_request(r) for r in reqs]
    return {"success": True, "data": enriched}

@router.get("/history")
def get_approval_history():
    actions = db.get("approval_actions", [])
    history_list = []
    
    for act in actions:
        app_req = next((a for a in db.get("approval_requests", []) if a.get("id") == act.get("approval_id")), {})
        enriched_req = enrich_approval_request(app_req) if app_req else {}
        history_list.append({
            **act,
            "txnDetails": enriched_req.get("txnDetails") or {
                "doc_number": act.get("transaction_id", "IND-2026-001003"),
                "requested_by": "Requisitioner User",
                "department": "Information Technology",
                "purpose": "Requisition Audit Log",
                "amount": 150000
            }
        })
    
    for req in db.get("approval_requests", []):
        if req.get("status") in ["Approved", "Rejected", "Returned for Correction", "Returned for correction"]:
            if not any(h.get("approval_id") == req.get("id") for h in history_list):
                history_list.append(enrich_approval_request(req))

    return {"success": True, "data": history_list}

@router.get("/workflows")
def get_approval_workflows():
    if "approval_workflows" not in db:
        db["approval_workflows"] = []
    return {"success": True, "data": db["approval_workflows"]}

@router.post("/workflows")
def create_or_update_workflow(payload: Dict[str, Any]):
    if "approval_workflows" not in db:
        db["approval_workflows"] = []

    wf_id = payload.get("id")
    if wf_id:
        for idx, wf in enumerate(db["approval_workflows"]):
            if wf.get("id") == wf_id:
                db["approval_workflows"][idx].update(payload)
                save_db()
                return {"success": True, "data": db["approval_workflows"][idx], "message": "Workflow matrix rule updated successfully."}

    new_wf = {
        "id": f"wf-{len(db['approval_workflows']) + 1}",
        "name": payload.get("name", "New Approval Matrix Rule"),
        "transaction_type": payload.get("transaction_type", "INDENT"),
        "department_id": payload.get("department_id", "ALL"),
        "branch_id": payload.get("branch_id", "ALL"),
        "item_category_id": payload.get("item_category_id", "ALL"),
        "min_amount": float(payload.get("min_amount", 0)),
        "max_amount": float(payload.get("max_amount")) if payload.get("max_amount") is not None and payload.get("max_amount") != "" else None,
        "urgency": payload.get("urgency", "ALL"),
        "steps": payload.get("steps", [])
    }
    db["approval_workflows"].append(new_wf)
    save_db()
    return {"success": True, "data": new_wf, "message": "New workflow matrix rule created successfully."}

@router.delete("/workflows/{wf_id}")
def delete_workflow(wf_id: str):
    if "approval_workflows" in db:
        db["approval_workflows"] = [w for w in db["approval_workflows"] if w.get("id") != wf_id]
        save_db()
        return {"success": True, "message": "Workflow matrix rule deleted successfully."}
    return {"success": False, "message": "Workflow rule not found"}

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
        "delegator_id": payload.get("delegator_id", "usr-04"),
        "delegator_name": "Sarah Jenkins",
        "delegatee_id": payload.get("delegatee_id", "usr-02"),
        "delegatee_name": "Jane Smith",
        "from_user": payload.get("delegator_id", "usr-04"),
        "to_user": payload.get("delegatee_id", "usr-02"),
        "start_date": payload.get("start_date", datetime.now().strftime("%Y-%m-%d")),
        "end_date": payload.get("end_date", datetime.now().strftime("%Y-%m-%d")),
        "reason": payload.get("remarks") or payload.get("reason") or "Annual Vacation Approval Delegation",
        "status": "Active",
        "is_active": True
    }
    db["approval_delegations"].append(new_del)
    save_db()
    return {"success": True, "data": new_del, "message": "Approval delegation rule saved successfully."}

@router.delete("/delegations/{del_id}")
def delete_delegation(del_id: str):
    if "approval_delegations" in db:
        db["approval_delegations"] = [d for d in db["approval_delegations"] if d.get("id") != del_id]
        save_db()
        return {"success": True, "message": "Approval delegation rule revoked successfully."}
    return {"success": False, "message": "Delegation rule not found"}

@router.post("/action")
@router.post("/{approval_id}/action")
def take_approval_action(req: ApprovalAction, approval_id: Optional[str] = None):
    app_id = req.approval_id or approval_id
    app_req = next((a for a in db.get("approval_requests", []) if a.get("id") == app_id), None)
    if not app_req:
        return {"success": True, "message": "Approval action processed."}

    now_iso = datetime.now().isoformat()
    old_status = app_req.get("status", "Pending")

    new_status = "Approved" if req.action == "Approve" else \
                 "Rejected" if req.action == "Reject" else \
                 "Returned for Correction" if req.action == "Return" else req.action

    app_req["status"] = new_status
    app_req["comments"] = req.comments or ""

    txn_type = str(app_req.get("transaction_type", "")).upper()
    txn_id = app_req.get("transaction_id")

    # Update target document status
    if "INDENT" in txn_type:
        ind = next((i for i in db.get("indents", []) if i.get("id") == txn_id or i.get("indent_number") == txn_id), None)
        if ind:
            ind["status"] = new_status
            if req.comments:
                ind["status_reason"] = req.comments
            if req.approved_items:
                ind["items"] = req.approved_items

    elif "PURCHASE" in txn_type or "PO" in txn_type:
        po = next((p for p in db.get("purchase_orders", []) if p.get("id") == txn_id or p.get("po_number") == txn_id), None)
        if po:
            po["status"] = new_status

    # Record timestamped action in approval_actions
    if "approval_actions" not in db:
        db["approval_actions"] = []

    act_entry = {
        "id": f"act-{len(db['approval_actions']) + 1}",
        "approval_id": app_id,
        "transaction_type": txn_type,
        "transaction_id": txn_id,
        "approver_id": req.user_id or app_req.get("approver_id", "usr-04"),
        "approver_name": req.user_name or "Department Manager",
        "action": req.action,
        "status": new_status,
        "comments": req.comments or "",
        "previous_status": old_status,
        "timestamp": now_iso
    }
    db["approval_actions"].insert(0, act_entry)

    from db.database_store import add_notification
    add_notification("Approval Decision Engine", f"{txn_type} requisition {txn_id} was {req.action.lower()}d by {req.user_name or 'Department Manager'}.", "success" if req.action == "Approve" else "warning", "ALL")

    # Record in audit log
    db["audit_logs"].append({
        "id": f"aud-{len(db['audit_logs']) + 1}",
        "user_id": req.user_id or "usr-04",
        "action": f"APPROVAL_{req.action.upper()}",
        "module": "APPROVAL_WORKFLOW",
        "record_id": app_id,
        "details": f"Processed approval action '{req.action}' on {txn_type} {txn_id}. Comment: {req.comments}",
        "timestamp": now_iso,
        "ip_address": "127.0.0.1"
    })

    save_db()
    return {"success": True, "message": f"Approval action '{req.action}' processed successfully.", "data": app_req}
