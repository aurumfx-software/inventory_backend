from fastapi import APIRouter, HTTPException
from db.database_store import db, save_db, get_next_doc_number
from schemas.schemas import IndentCreate
from datetime import datetime
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/indents", tags=["Indents"])

@router.get("")
def get_indents():
    # Enrich indents with department names and user names
    results = []
    for indent in db.get("indents", []):
        dept = next((d for d in db.get("departments", []) if d["id"] == indent.get("department_id")), {})
        usr = next((u for u in db.get("users", []) if u["id"] == indent.get("requested_by")), {})
        
        # Ensure cost_centre / cost_centre_or_project is populated
        cost_centre_val = indent.get("cost_centre_or_project") or indent.get("cost_centre") or "IT-001"

        results.append({
            **indent,
            "department_name": dept.get("name", "Information Technology"),
            "requested_by_name": usr.get("name", "Employee User"),
            "cost_centre_or_project": cost_centre_val,
            "cost_centre": cost_centre_val
        })
    return {"success": True, "data": results}

@router.post("")
def create_indent(payload: dict):
    # Validations per requirements:
    # 1. Purpose is mandatory
    purpose = payload.get("purpose", "").strip()
    if not purpose:
        raise HTTPException(status_code=400, detail="Purpose is mandatory for material indents.")

    # 2. At least one item is required
    items = payload.get("items", [])
    if not items:
        raise HTTPException(status_code=400, detail="At least one item is required in the indent.")

    # 3. Urgent/Emergency requests require justification
    priority = payload.get("priority", "Normal")
    priority_justification = payload.get("priority_justification", "").strip()
    if priority in ["Urgent", "Emergency"] and not priority_justification:
        raise HTTPException(status_code=400, detail="Urgent or Emergency requests require a justification explanation.")

    # Check for inactive items or invalid quantities
    for item in items:
        qty = float(item.get("requested_qty", 0))
        if qty <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")
        item_obj = next((i for i in db.get("items", []) if i["id"] == item.get("item_id")), {})
        if item_obj and item_obj.get("is_active") is False:
            raise HTTPException(status_code=400, detail=f"Item {item_obj.get('item_name')} is inactive and cannot be requested.")

    indent_num = get_next_doc_number("IND")
    new_id = f"ind-{len(db['indents']) + 1002}"
    now = datetime.now().isoformat()
    cost_centre_val = payload.get("cost_centre_or_project") or payload.get("cost_centre") or "IT-001"

    # Calculate total estimated amount
    total_est = sum(float(i.get("requested_qty", 1)) * float(i.get("estimated_rate", 0)) for i in items)

    new_indent = {
        "id": new_id,
        "indent_number": indent_num,
        "request_date": datetime.now().strftime("%Y-%m-%d"),
        "department_id": payload.get("department_id") or "dept-01",
        "requested_by": payload.get("requested_by") or "usr-05",
        "required_date": payload.get("required_date") or datetime.now().strftime("%Y-%m-%d"),
        "purpose": purpose,
        "priority": priority,
        "priority_justification": priority_justification,
        "cost_centre_or_project": cost_centre_val,
        "cost_centre": cost_centre_val,
        "remarks": payload.get("remarks") or "",
        "status": payload.get("status") or "Submitted",
        "total_estimated_amount": total_est if total_est > 0 else 150000,
        "items": items,
        "created_at": now
    }
    
    db["indents"].append(new_indent)

    # Workflow request creation
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
        "user_id": payload.get("requested_by") or "usr-05",
        "action": "INDENT_SUBMITTED" if new_indent["status"] == "Submitted" else "INDENT_DRAFT_CREATED",
        "module": "PROCUREMENT",
        "record_id": new_id,
        "details": f"Created Indent Requisition {indent_num} with Cost Centre/Project {cost_centre_val}",
        "timestamp": now,
        "ip_address": "127.0.0.1"
    })

    save_db()
    return {"success": True, "data": new_indent}

@router.get("/stock-review-queue")
def get_stock_review_queue():
    indents_list = [i for i in db.get("indents", []) if i.get("status") in ["Approved", "Submitted", "Partially fulfilled", "Under review"]]
    
    enriched_queue = []
    for indent in indents_list:
        dept = next((d for d in db.get("departments", []) if d["id"] == indent.get("department_id")), {})
        usr = next((u for u in db.get("users", []) if u["id"] == indent.get("requested_by")), {})
        
        enriched_items = []
        for idx, item in enumerate(indent.get("items", [])):
            item_id = item.get("item_id")
            item_master = next((im for im in db.get("items", []) if im["id"] == item_id), {})
            
            # Calculate live available stock from inventory_balances
            balances = [b for b in db.get("inventory_balances", []) if b.get("item_id") == item_id]
            if balances:
                total_avail = float(sum(b.get("available_qty", 0) for b in balances))
                total_on_hand = float(sum(b.get("on_hand_qty", 0) for b in balances))
                total_reserved = float(sum(b.get("reserved_qty", 0) for b in balances))
            else:
                total_avail = float(item.get("available_qty") or item_master.get("available_stock") or 0)
                total_on_hand = float(item.get("on_hand_qty") or item_master.get("on_hand_stock") or 0)
                total_reserved = float(item.get("reserved_qty") or 0)
            
            req_qty = float(item.get("requested_qty", 1))
            
            # Determine suggested action
            if total_avail >= req_qty:
                suggested_action = "issue-full"
            elif total_avail <= 0:
                suggested_action = "purchase-full"
            else:
                suggested_action = "partial"

            enriched_items.append({
                **item,
                "id": item.get("id") or f"{indent['id']}-item-{idx+1}",
                "item_code": item.get("item_code") or item_master.get("item_code", f"ITM-{idx+1}"),
                "item_name": item.get("item_name") or item_master.get("item_name", "Material Item"),
                "available_qty": total_avail,
                "on_hand_qty": total_on_hand,
                "reserved_qty": total_reserved,
                "suggested_action": item.get("suggested_action") or suggested_action,
                "review_status": item.get("review_status") or "Under Review",
                "issue_from_stock_qty": item.get("issue_from_stock_qty", min(total_avail, req_qty)),
                "purchase_req_qty": item.get("purchase_req_qty", max(0, req_qty - total_avail)),
                "valuation_rate": item_master.get("valuation_rate") or item.get("estimated_rate") or 100
            })

        enriched_queue.append({
            **indent,
            "department_name": dept.get("name", "Information Technology"),
            "requested_by_name": usr.get("name", "Requisitioner User"),
            "items": enriched_items
        })

    return {"success": True, "data": enriched_queue}

@router.post("/stock-review-action")
def execute_stock_review_action(payload: Dict[str, Any]):
    indent_id = payload.get("indent_id")
    line_item_id = payload.get("line_item_id")
    action_choice = payload.get("action_choice", payload.get("action"))  # 'issue-full' | 'purchase-full' | 'partial' | 'substitute' | 'reject'
    issue_qty = float(payload.get("issue_qty", 0))
    purchase_qty = float(payload.get("purchase_qty", 0))
    substitute_item_id = payload.get("substitute_item_id")
    reason = payload.get("reason", "")
    user_id = payload.get("user_id", "usr-03")

    indent = next((i for i in db.get("indents", []) if i["id"] == indent_id), None)
    if not indent:
        return {"success": False, "message": "Indent not found"}

    items = indent.get("items", [])
    target_line = next((item for item in items if item.get("id") == line_item_id or item.get("item_id") == line_item_id), None)
    if not target_line and items:
        target_line = items[0]

    if target_line:
        now_iso = datetime.now().isoformat()
        item_id = target_line.get("item_id")
        item_master = next((im for im in db.get("items", []) if im["id"] == item_id), {})
        item_name = item_master.get("item_name", "Item")

        # 1. Create Stock Issue Request if stock is to be issued
        if issue_qty > 0:
            if "stock_issues" not in db:
                db["stock_issues"] = []
            
            stock_issue_doc = {
                "id": f"iss-{len(db['stock_issues']) + 1001}",
                "issue_number": f"ISS-{datetime.now().year}-{str(len(db['stock_issues']) + 1001).zfill(6)}",
                "indent_id": indent_id,
                "indent_number": indent.get("indent_number"),
                "department_id": indent.get("department_id"),
                "item_id": item_id,
                "item_name": item_name,
                "requested_qty": target_line.get("requested_qty", issue_qty),
                "issued_qty": issue_qty,
                "warehouse_id": "wh-01",
                "status": "Approved for Issue",
                "created_at": now_iso
            }
            db["stock_issues"].append(stock_issue_doc)

        # 2. Create Procurement RFQ Requirement if purchase is required
        if purchase_qty > 0:
            if "rfqs" not in db:
                db["rfqs"] = []

            rfq_doc = {
                "id": f"rfq-{len(db['rfqs']) + 1001}",
                "rfq_number": f"RFQ-{datetime.now().year}-{str(len(db['rfqs']) + 1001).zfill(6)}",
                "indent_id": indent_id,
                "indent_number": indent.get("indent_number"),
                "item_id": item_id,
                "item_name": item_name,
                "required_qty": purchase_qty,
                "target_date": indent.get("required_date"),
                "status": "Draft",
                "created_at": now_iso
            }
            db["rfqs"].append(rfq_doc)

        # 3. Update Line Item Review Status
        status_label = "Approved for Issue" if action_choice == "issue-full" else \
                       "Split Created" if action_choice == "partial" else \
                       "Converted to RFQ" if action_choice == "purchase-full" else \
                       "Substituted" if action_choice == "substitute" else "Rejected"

        target_line["review_status"] = status_label
        target_line["issue_from_stock_qty"] = issue_qty
        target_line["purchase_req_qty"] = purchase_qty
        target_line["action_reason"] = reason
        if substitute_item_id:
            target_line["substitute_item_id"] = substitute_item_id

        # 4. Check overall Indent status progression
        all_statuses = [i.get("review_status") for i in items if i.get("review_status") and i.get("review_status") != "Under Review"]
        if len(all_statuses) == len(items):
            if any(i.get("purchase_req_qty", 0) > 0 for i in items):
                indent["status"] = "Partially fulfilled"
            elif all(i.get("review_status") == "Approved for Issue" for i in items):
                indent["status"] = "Fulfilled"

        # 5. Audit Log Entry
        db["audit_logs"].append({
            "id": f"aud-{len(db['audit_logs']) + 1}",
            "user_id": user_id,
            "action": "STOCK_AVAILABILITY_REVIEW",
            "module": "INVENTORY_STORE",
            "record_id": indent_id,
            "details": f"Stock review action '{action_choice}' executed for item {item_name}. Issued from stock: {issue_qty}, Purchase required: {purchase_qty}.",
            "timestamp": now_iso,
            "ip_address": "127.0.0.1"
        })

        save_db()
        return {
            "success": True,
            "message": f"Stock review action processed: Issued {issue_qty} units from stock, created procurement request for {purchase_qty} units.",
            "data": indent
        }

    return {"success": False, "message": "Line item not found in indent"}

@router.get("/{indent_id}")
def get_indent(indent_id: str):
    indent = next((i for i in db["indents"] if i["id"] == indent_id), None)
    if indent:
        dept = next((d for d in db.get("departments", []) if d["id"] == indent.get("department_id")), {})
        usr = next((u for u in db.get("users", []) if u["id"] == indent.get("requested_by")), {})
        cost_centre_val = indent.get("cost_centre_or_project") or indent.get("cost_centre") or "IT-001"

        return {
            "success": True,
            "data": {
                **indent,
                "department_name": dept.get("name", "Information Technology"),
                "requested_by_name": usr.get("name", "Employee User"),
                "cost_centre_or_project": cost_centre_val,
                "cost_centre": cost_centre_val
            }
        }
    return {"success": False, "message": "Indent not found"}

@router.put("/{indent_id}")
def update_indent(indent_id: str, payload: dict):
    indent = next((i for i in db["indents"] if i["id"] == indent_id), None)
    if not indent:
        return {"success": False, "message": "Indent not found"}

    cost_centre_val = payload.get("cost_centre_or_project") or payload.get("cost_centre") or indent.get("cost_centre_or_project") or "IT-001"
    
    indent.update({
        "department_id": payload.get("department_id") or indent.get("department_id"),
        "required_date": payload.get("required_date") or indent.get("required_date"),
        "purpose": payload.get("purpose") or indent.get("purpose"),
        "priority": payload.get("priority") or indent.get("priority"),
        "priority_justification": payload.get("priority_justification") or indent.get("priority_justification"),
        "cost_centre_or_project": cost_centre_val,
        "cost_centre": cost_centre_val,
        "remarks": payload.get("remarks") if payload.get("remarks") is not None else indent.get("remarks"),
        "items": payload.get("items") or indent.get("items", [])
    })

    if payload.get("items"):
        indent["total_estimated_amount"] = sum(float(i.get("requested_qty", 1)) * float(i.get("estimated_rate", 0)) for i in payload["items"])

    db["audit_logs"].append({
        "id": f"aud-{len(db['audit_logs']) + 1}",
        "user_id": payload.get("updated_by") or "usr-05",
        "action": "INDENT_UPDATED",
        "module": "PROCUREMENT",
        "record_id": indent_id,
        "details": f"Updated Indent {indent.get('indent_number')} Cost Centre/Project: {cost_centre_val}",
        "timestamp": datetime.now().isoformat(),
        "ip_address": "127.0.0.1"
    })

    save_db()
    return {"success": True, "data": indent}

@router.post("/{indent_id}/submit")
def submit_indent(indent_id: str):
    indent = next((i for i in db["indents"] if i["id"] == indent_id), None)
    if indent:
        indent["status"] = "Submitted"
        db["audit_logs"].append({
            "id": f"aud-{len(db['audit_logs']) + 1}",
            "user_id": "usr-05",
            "action": "INDENT_SUBMITTED",
            "module": "PROCUREMENT",
            "record_id": indent_id,
            "details": f"Submitted Indent Requisition {indent.get('indent_number')}",
            "timestamp": datetime.now().isoformat(),
            "ip_address": "127.0.0.1"
        })
        save_db()
        return {"success": True, "data": indent}
    return {"success": False, "message": "Indent not found"}

@router.post("/{indent_id}/cancel")
def cancel_indent(indent_id: str, payload: Optional[dict] = None):
    indent = next((i for i in db["indents"] if i["id"] == indent_id), None)
    if indent:
        reason = payload.get("reason", "Cancelled by user") if payload else "Cancelled"
        indent["status"] = "Cancelled"
        indent["cancellation_reason"] = reason
        db["audit_logs"].append({
            "id": f"aud-{len(db['audit_logs']) + 1}",
            "user_id": payload.get("user_id") if payload else "usr-05",
            "action": "INDENT_CANCELLED",
            "module": "PROCUREMENT",
            "record_id": indent_id,
            "details": f"Cancelled Indent {indent.get('indent_number')}. Reason: {reason}",
            "timestamp": datetime.now().isoformat(),
            "ip_address": "127.0.0.1"
        })
        save_db()
        return {"success": True, "data": indent, "message": f"Indent {indent.get('indent_number')} cancelled successfully."}
    return {"success": False, "message": "Indent not found"}

@router.post("/{indent_id}/copy")
def copy_indent(indent_id: str):
    original = next((i for i in db["indents"] if i["id"] == indent_id), None)
    if original:
        cost_centre_val = original.get("cost_centre_or_project") or original.get("cost_centre") or "IT-001"
        copied = {
            **original,
            "id": f"ind-{len(db['indents'])+1002}",
            "indent_number": get_next_doc_number("IND"),
            "status": "Draft",
            "purpose": f"Copy of {original.get('indent_number')}: {original.get('purpose', '')}",
            "cost_centre_or_project": cost_centre_val,
            "cost_centre": cost_centre_val,
            "created_at": datetime.now().isoformat()
        }
        db["indents"].append(copied)
        save_db()
        return {"success": True, "data": copied}
    return {"success": False, "message": "Original indent not found"}

@router.post("/{indent_id}/status")
def transition_indent_status(indent_id: str, payload: dict):
    indent = next((i for i in db["indents"] if i["id"] == indent_id), None)
    if not indent:
        return {"success": False, "message": "Indent not found"}

    new_status = payload.get("status", "Submitted")
    reason = payload.get("reason", "")
    indent["status"] = new_status
    if reason:
        indent["status_reason"] = reason

    db["audit_logs"].append({
        "id": f"aud-{len(db['audit_logs']) + 1}",
        "user_id": payload.get("user_id") or "usr-05",
        "action": f"INDENT_STATUS_{new_status.upper().replace(' ', '_')}",
        "module": "PROCUREMENT",
        "record_id": indent_id,
        "details": f"Transitioned Indent {indent.get('indent_number')} status to '{new_status}'. Reason: {reason}",
        "timestamp": datetime.now().isoformat(),
        "ip_address": "127.0.0.1"
    })

    save_db()
    return {"success": True, "data": indent, "message": f"Indent status transitioned to '{new_status}'."}

@router.get("/{indent_id}/history")
def get_indent_history(indent_id: str):
    history = [l for l in db["audit_logs"] if l.get("record_id") == indent_id]
    return {"success": True, "data": history}

@router.delete("/{indent_id}")
def delete_indent(indent_id: str):
    initial_len = len(db["indents"])
    db["indents"] = [i for i in db["indents"] if i["id"] != indent_id]
    if len(db["indents"]) < initial_len:
        save_db()
        return {"success": True, "message": "Indent deleted successfully"}
    return {"success": False, "message": "Indent not found"}
