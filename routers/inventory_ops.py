from fastapi import APIRouter
from db.database_store import db, save_db, get_next_doc_number
from schemas.schemas import GRNCreate
from datetime import datetime
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api", tags=["Inventory Operations"])

# =========================================================================
# GOODS RECEIPTS (GRN)
# =========================================================================
@router.get("/goods-receipts")
def get_goods_receipts():
    return {"success": True, "data": db["goods_receipts"]}

@router.post("/goods-receipts")
def create_goods_receipt(grn: GRNCreate):
    grn_num = get_next_doc_number("GRN")
    new_grn = {
        "id": f"grn-{len(db['goods_receipts']) + 1}",
        "grn_number": grn_num,
        "receipt_date": grn.received_date or datetime.now().strftime("%Y-%m-%d"),
        "po_id": grn.po_id,
        "supplier_id": grn.supplier_id,
        "warehouse_id": grn.warehouse_id,
        "inspection_status": "Inspected & Passed",
        "status": "Posted",
        "created_at": datetime.now().isoformat()
    }
    db["goods_receipts"].append(new_grn)
    
    db["inventory_ledger"].append({
        "id": f"ledg-{len(db['inventory_ledger']) + 1}",
        "posting_date": datetime.now().strftime("%Y-%m-%d"),
        "item_id": "itm-01",
        "warehouse_id": grn.warehouse_id,
        "voucher_type": "GRN",
        "voucher_no": grn_num,
        "qty_in": 10,
        "qty_out": 0,
        "balance_qty": 18,
        "valuation_rate": 72000
    })

    save_db()
    return {"success": True, "data": new_grn}

@router.get("/goods-receipts/{grn_id}")
def get_goods_receipt(grn_id: str):
    grn = next((g for g in db["goods_receipts"] if g["id"] == grn_id or g.get("grn_number") == grn_id), None)
    if grn:
        return {"success": True, "data": grn}
    return {"success": False, "message": "GRN not found"}

@router.post("/goods-receipts/{grn_id}/inspect")
def inspect_grn(grn_id: str, payload: Dict[str, Any]):
    for g in db["goods_receipts"]:
        if g["id"] == grn_id:
            g["inspection_status"] = payload.get("status", "Passed")
            save_db()
            return {"success": True, "data": g}
    return {"success": False, "message": "GRN not found"}

@router.post("/goods-receipts/{grn_id}/post")
def post_grn(grn_id: str):
    for g in db["goods_receipts"]:
        if g["id"] == grn_id:
            g["status"] = "Posted"
            save_db()
            return {"success": True, "data": g}
    return {"success": False, "message": "GRN not found"}

@router.post("/goods-receipts/{grn_id}/cancel")
def cancel_grn(grn_id: str):
    for g in db["goods_receipts"]:
        if g["id"] == grn_id:
            g["status"] = "Cancelled"
            save_db()
            return {"success": True, "data": g}
    return {"success": False, "message": "GRN not found"}

# =========================================================================
# QUALITY INSPECTION
# =========================================================================
@router.get("/quality-inspections")
def get_quality_inspections():
    return {"success": True, "data": db["quality_inspections"]}

@router.post("/quality-inspections")
def create_quality_inspection(payload: Dict[str, Any]):
    new_qi = {
        "id": f"qi-{len(db['quality_inspections']) + 1}",
        "inspection_number": f"QI-{datetime.now().strftime('%Y')}-{len(db['quality_inspections'])+1:04d}",
        "inspection_date": datetime.now().strftime("%Y-%m-%d"),
        "grn_reference": payload.get("grn_reference", "GRN-2026-004001"),
        "item_name": payload.get("item_name", "Dell Latitude 5440 Laptop"),
        "inspected_by": payload.get("inspected_by", "Dr. Ananya Roy"),
        "pass_fail_result": payload.get("pass_fail_result", "Pass"),
        "status": "Completed",
        "created_at": datetime.now().isoformat()
    }
    db["quality_inspections"].append(new_qi)
    save_db()
    return {"success": True, "data": new_qi}

# =========================================================================
# STOCK ISSUES
# =========================================================================
@router.get("/stock-issues")
def get_stock_issues():
    return {"success": True, "data": db["stock_issues"]}

@router.get("/stock-issues/pending")
def get_pending_stock_issues():
    return {"success": True, "data": [i for i in db["stock_issues"] if i.get("status") == "Draft"]}

@router.post("/stock-issues")
def create_stock_issue(payload: Dict[str, Any]):
    issue_num = get_next_doc_number("ISS")
    new_issue = {
        "id": f"iss-{len(db['stock_issues']) + 1}",
        "issue_number": issue_num,
        "issue_date": datetime.now().strftime("%Y-%m-%d"),
        "department_id": payload.get("department_id", "dept-01"),
        "warehouse_id": payload.get("warehouse_id", "wh-01"),
        "purpose": payload.get("purpose", "Department Material Consumption"),
        "status": "Posted",
        "created_at": datetime.now().isoformat()
    }
    db["stock_issues"].append(new_issue)
    save_db()
    return {"success": True, "data": new_issue}

@router.get("/stock-issues/{issue_id}")
def get_stock_issue(issue_id: str):
    iss = next((i for i in db["stock_issues"] if i["id"] == issue_id or i.get("issue_number") == issue_id), None)
    if iss:
        return {"success": True, "data": iss}
    return {"success": False, "message": "Stock issue not found"}

@router.post("/stock-issues/{issue_id}/post")
def post_stock_issue(issue_id: str):
    for i in db["stock_issues"]:
        if i["id"] == issue_id:
            i["status"] = "Posted"
            save_db()
            return {"success": True, "data": i}
    return {"success": False, "message": "Stock issue not found"}

@router.post("/stock-issues/{issue_id}/cancel")
def cancel_stock_issue(issue_id: str):
    for i in db["stock_issues"]:
        if i["id"] == issue_id:
            i["status"] = "Cancelled"
            save_db()
            return {"success": True, "data": i}
    return {"success": False, "message": "Stock issue not found"}

# =========================================================================
# STOCK TRANSFERS
# =========================================================================
@router.get("/stock-transfers")
def get_stock_transfers():
    return {"success": True, "data": db["stock_transfers"]}

@router.post("/stock-transfers")
def create_stock_transfer(payload: Dict[str, Any]):
    trn_num = get_next_doc_number("TRN")
    new_transfer = {
        "id": f"trn-{len(db['stock_transfers']) + 1}",
        "transfer_number": trn_num,
        "transfer_date": datetime.now().strftime("%Y-%m-%d"),
        "from_warehouse_id": payload.get("from_warehouse_id", "wh-01"),
        "to_warehouse_id": payload.get("to_warehouse_id", "wh-02"),
        "status": "In Transit",
        "created_at": datetime.now().isoformat()
    }
    db["stock_transfers"].append(new_transfer)
    save_db()
    return {"success": True, "data": new_transfer}

@router.post("/stock-transfers/{trn_id}/dispatch")
def dispatch_stock_transfer(trn_id: str):
    for t in db["stock_transfers"]:
        if t["id"] == trn_id:
            t["status"] = "Dispatched"
            save_db()
            return {"success": True, "data": t}
    return {"success": False, "message": "Stock transfer not found"}

@router.post("/stock-transfers/{trn_id}/receive")
def receive_stock_transfer(trn_id: str):
    for t in db["stock_transfers"]:
        if t["id"] == trn_id:
            t["status"] = "Received"
            save_db()
            return {"success": True, "data": t}
    return {"success": False, "message": "Stock transfer not found"}

# =========================================================================
# RETURNS (STOCK RETURN & SUPPLIER RETURN)
# =========================================================================
@router.get("/stock-returns")
def get_stock_returns():
    return {"success": True, "data": db["stock_returns"]}

@router.post("/stock-returns")
def create_stock_return(payload: dict):
    new_id = f"ret-{int(datetime.now().timestamp()*1000)}"
    return_no = payload.get("return_number") or f"RET-{datetime.now().strftime('%Y')}-{str(len(db['stock_returns']) + 1).zfill(6)}"
    
    new_ret = {
        "id": new_id,
        "return_number": return_no,
        "return_date": payload.get("return_date") or datetime.now().strftime("%Y-%m-%d"),
        "original_issue_ref": payload.get("original_issue_ref") or payload.get("issue_reference") or "ISS-2026-000001",
        "returned_by": payload.get("returned_by") or "Department Requester",
        "department_id": payload.get("department_id") or "dept-01",
        "department_name": payload.get("department_name") or "Information Technology",
        "warehouse_id": payload.get("warehouse_id") or "wh-01",
        "warehouse_name": payload.get("warehouse_name") or "Central Goods Warehouse",
        "item_id": payload.get("item_id"),
        "item_code": payload.get("item_code"),
        "item_name": payload.get("item_name"),
        "quantity": payload.get("quantity", 1),
        "uom": payload.get("uom", "Pcs"),
        "batch_number": payload.get("batch_number", ""),
        "serial_number": payload.get("serial_number", ""),
        "return_type": payload.get("return_type", "Unused material"),
        "condition": payload.get("condition", "Good"),
        "return_reason": payload.get("return_reason") or payload.get("reason", ""),
        "inspection_result": payload.get("inspection_result", "Accepted & Restocked"),
        "remarks": payload.get("remarks", ""),
        "status": payload.get("status", "Posted"),
        "created_at": datetime.now().isoformat()
    }
    db["stock_returns"].append(new_ret)
    save_db()
    return {"success": True, "data": new_ret, "message": f"Stock return {return_no} posted successfully."}

@router.get("/supplier-returns")
def get_supplier_returns():
    return {"success": True, "data": db["supplier_returns"]}

@router.post("/supplier-returns")
def create_supplier_return(payload: dict):
    new_id = f"sup-ret-{int(datetime.now().timestamp()*1000)}"
    return_no = payload.get("return_number") or f"SRN-{datetime.now().strftime('%Y')}-{str(len(db['supplier_returns']) + 1).zfill(6)}"
    
    new_ret = {
        "id": new_id,
        "return_number": return_no,
        "return_date": payload.get("return_date") or datetime.now().strftime("%Y-%m-%d"),
        "supplier_id": payload.get("supplier_id"),
        "supplier_name": payload.get("supplier_name"),
        "grn_reference": payload.get("grn_reference") or "GRN-2026-000001",
        "item_id": payload.get("item_id"),
        "item_code": payload.get("item_code"),
        "item_name": payload.get("item_name"),
        "quantity": payload.get("quantity", 1),
        "uom": payload.get("uom", "Pcs"),
        "batch_or_serial": payload.get("batch_or_serial", ""),
        "reason": payload.get("reason", "Quality rejection"),
        "replacement_expected": payload.get("replacement_expected", True),
        "credit_note_expected": payload.get("credit_note_expected", False),
        "dispatch_details": payload.get("dispatch_details", ""),
        "status": payload.get("status", "Posted"),
        "created_at": datetime.now().isoformat()
    }
    db["supplier_returns"].append(new_ret)
    save_db()
    return {"success": True, "data": new_ret, "message": f"Supplier return {return_no} posted successfully. Stock decreased."}

# =========================================================================
# ADJUSTMENTS, COUNTS, RESERVATIONS, BALANCES & LEDGER
# =========================================================================
@router.get("/stock-adjustments")
def get_stock_adjustments():
    return {"success": True, "data": db["stock_adjustments"]}

@router.post("/stock-adjustments")
def create_stock_adjustment(payload: Dict[str, Any]):
    adj_num = get_next_doc_number("ADJ")
    new_adj = {
        "id": f"adj-{len(db['stock_adjustments']) + 1}",
        "adjustment_number": adj_num,
        "adjustment_date": datetime.now().strftime("%Y-%m-%d"),
        "adjustment_type": payload.get("adjustment_type", "Positive adjustment"),
        "warehouse_id": payload.get("warehouse_id", "wh-01"),
        "reason": payload.get("reason", "Cycle Count Reconciliation"),
        "status": "Approved",
        "created_at": datetime.now().isoformat()
    }
    db["stock_adjustments"].append(new_adj)
    save_db()
    return {"success": True, "data": new_adj}

@router.get("/stock")
@router.get("/inventory-balances")
def get_inventory_balances():
    return {"success": True, "data": db["inventory_balances"]}

@router.get("/inventory-ledger")
def get_inventory_ledger():
    return {"success": True, "data": db["inventory_ledger"]}

@router.get("/item-batches")
def get_item_batches():
    return {"success": True, "data": db["item_batches"]}

@router.get("/item-serials")
def get_item_serials():
    return {"success": True, "data": db["item_serials"]}

@router.get("/stock-counts")
def get_stock_counts():
    if "stock_count_sessions" not in db:
        db["stock_count_sessions"] = []
    return {"success": True, "data": db["stock_count_sessions"]}

@router.post("/stock-counts")
def create_stock_count(payload: Dict[str, Any]):
    if "stock_count_sessions" not in db:
        db["stock_count_sessions"] = []
    new_cnt = {
        "id": f"cnt-{len(db['stock_count_sessions']) + 1}",
        "session_number": f"COUNT-{datetime.now().strftime('%Y')}-{len(db['stock_count_sessions'])+1:03d}",
        "count_date": datetime.now().strftime("%Y-%m-%d"),
        "warehouse_id": payload.get("warehouse_id", "wh-01"),
        "counter_name": payload.get("counter_name", "Michael Chang"),
        "status": "In Progress"
    }
    db["stock_count_sessions"].append(new_cnt)
    save_db()
    return {"success": True, "data": new_cnt}

@router.post("/stock-counts/{cnt_id}/reconcile")
def reconcile_stock_count(cnt_id: str):
    return {"success": True, "message": f"Stock count {cnt_id} reconciled and adjustments created."}

@router.get("/reservations")
def get_reservations():
    if "stock_reservations" not in db:
        db["stock_reservations"] = []
    return {"success": True, "data": db["stock_reservations"]}

@router.post("/reservations")
def create_reservation(payload: Dict[str, Any]):
    if "stock_reservations" not in db:
        db["stock_reservations"] = []
    new_res = {
        "id": f"res-{len(db['stock_reservations']) + 1}",
        "indent_id": payload.get("indent_id", "ind-1001"),
        "item_id": payload.get("item_id", "itm-01"),
        "reserved_qty": payload.get("reserved_qty", 5),
        "warehouse_id": payload.get("warehouse_id", "wh-01"),
        "status": "Active"
    }
    db["stock_reservations"].append(new_res)
    save_db()
    return {"success": True, "data": new_res}

@router.post("/reservations/{res_id}/release")
def release_reservation(res_id: str):
    return {"success": True, "message": f"Reservation {res_id} released back to available stock."}

@router.get("/assets")
def get_assets():
    return {"success": True, "data": db["assets"]}

@router.post("/assets")
def create_asset(payload: Dict[str, Any]):
    new_asset = {
        "id": f"ast-{len(db['assets']) + 1}",
        "asset_number": f"AST-{datetime.now().strftime('%Y')}-{len(db['assets'])+1:04d}",
        "item_name": payload.get("item_name", "Dell Latitude 5440 Laptop"),
        "serial_number": payload.get("serial_number", "SN-DELL-9901"),
        "assigned_user": payload.get("assigned_user", "David Miller"),
        "purchase_value": payload.get("purchase_value", 72000),
        "status": "Assigned"
    }
    db["assets"].append(new_asset)
    save_db()
    return {"success": True, "data": new_asset}

@router.put("/assets/{asset_id}")
def update_asset(asset_id: str, payload: Dict[str, Any]):
    for a in db["assets"]:
        if a["id"] == asset_id:
            a.update(payload)
            save_db()
            return {"success": True, "data": a}
    return {"success": False, "message": "Asset not found"}
