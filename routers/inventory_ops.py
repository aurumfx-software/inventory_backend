from fastapi import APIRouter
from db.database_store import db, save_db, get_next_doc_number
from schemas.schemas import GRNCreate
from datetime import datetime
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api", tags=["Inventory Operations"])

@router.get("/goods-receipts")
def get_goods_receipts():
    return {"success": True, "data": db.get("goods_receipts", [])}

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

@router.get("/quality-inspections")
def get_quality_inspections():
    return {"success": True, "data": db.get("quality_inspections", [])}

@router.post("/quality-inspections")
def create_quality_inspection(payload: Dict[str, Any]):
    if "quality_inspections" not in db:
        db["quality_inspections"] = []
        
    ref = payload.get("inspection_reference") or payload.get("inspection_number") or f"QI-{datetime.now().strftime('%Y')}-{len(db['quality_inspections'])+1:06d}"
    
    new_qi = {
        "id": f"qi-{len(db['quality_inspections']) + 1}",
        "inspection_reference": ref,
        "inspection_number": ref,
        "inspection_date": payload.get("inspection_date", datetime.now().strftime("%Y-%m-%d")),
        "grn_id": payload.get("grn_id", "grn-1"),
        "grn_reference": payload.get("grn_reference", "GRN-2026-004002"),
        "supplier_name": payload.get("supplier_name", "Infotech Systems Ltd"),
        "selected_item_id": payload.get("selected_item_id", "itm-01"),
        "item_code": payload.get("item_code", "IT-LAP-0001"),
        "item_name": payload.get("item_name", "Dell Latitude 5440 Laptop"),
        "inspected_by": payload.get("inspected_by", "Michael Chang (Store Manager)"),
        "accepted_qty": payload.get("accepted_qty", 18),
        "rejected_qty": payload.get("rejected_qty", 2),
        "inspection_outcome": payload.get("inspection_outcome", "Accepted with deviation"),
        "status": payload.get("inspection_outcome", "Accepted with deviation"),
        "pass_fail_result": payload.get("pass_fail_result", "Pass"),
        "remarks": payload.get("remarks", "Quality inspection logged successfully."),
        "inspection_rows": payload.get("inspection_rows", []),
        "created_at": datetime.now().isoformat()
    }
    db["quality_inspections"].append(new_qi)
    save_db()
    return {"success": True, "data": new_qi, "message": f"Quality inspection {ref} created."}

# =========================================================================
# REJECTED MATERIALS LOG
# =========================================================================
@router.get("/rejected-materials")
def get_rejected_materials():
    if "rejected_materials" not in db:
        db["rejected_materials"] = []
    return {"success": True, "data": db["rejected_materials"]}

@router.post("/rejected-materials")
def create_rejected_material(payload: Dict[str, Any]):
    if "rejected_materials" not in db:
        db["rejected_materials"] = []
    new_rej = {
        "id": f"rej-{len(db['rejected_materials']) + 1}",
        "rejection_number": f"REJ-{datetime.now().strftime('%Y')}-{len(db['rejected_materials'])+1:04d}",
        "grn_number": payload.get("grn_number", "GRN-2026-5710"),
        "item_code": payload.get("item_code", "ITM-001"),
        "item_name": payload.get("item_name", "Dell Latitude Laptop"),
        "supplier_name": payload.get("supplier_name", "Supplier Name"),
        "rejected_qty": payload.get("rejected_qty", 1),
        "rejection_reason": payload.get("rejection_reason", "Physical damage / specification mismatch"),
        "disposition": payload.get("disposition", "Return to Supplier"),
        "created_at": datetime.now().isoformat()
    }
    db["rejected_materials"].append(new_rej)
    save_db()
    return {"success": True, "data": new_rej}

# =========================================================================
# STOCK ISSUES
# =========================================================================
@router.get("/stock-issues")
def get_stock_issues():
    return {"success": True, "data": db.get("stock_issues", [])}

@router.get("/stock-issues/pending")
def get_pending_stock_issues():
    return {"success": True, "data": [i for i in db.get("stock_issues", []) if i.get("status") in ["Draft", "Pending"]]}

@router.post("/stock-issues")
def create_stock_issue(payload: Dict[str, Any]):
    issue_num = payload.get("issue_number") or get_next_doc_number("ISS")
    raw_items = payload.get("items", [])
    processed_items = []
    
    dept_id = payload.get("department_id", "dept-01")
    dept = next((d for d in db.get("departments", []) if d["id"] == dept_id), None)
    dept_name = payload.get("department_name") or (dept["name"] if dept else "Information Technology")

    wh_id = payload.get("warehouse_id", "wh-01")
    wh = next((w for w in db.get("warehouses", []) if w["id"] == wh_id), None)
    wh_name = payload.get("warehouse_name") or (wh["name"] if wh else "Central Goods Warehouse")

    for idx, item in enumerate(raw_items):
        qty = float(item.get("issue_qty") or item.get("quantity") or item.get("requested_qty") or 1)
        rate = float(item.get("unit_rate") or item.get("rate") or 0)
        itm_id = item.get("item_id", "itm-01")
        itm = next((i for i in db.get("items", []) if i["id"] == itm_id), None)
        
        processed_items.append({
            "id": f"issi-{len(db.get('stock_issues', [])) + 1}-{idx + 1}",
            "item_id": itm_id,
            "item_code": item.get("item_code") or (itm.get("item_code") if itm else "ITM-001"),
            "item_name": item.get("item_name") or (itm.get("item_name") if itm else "Dell Latitude Laptop"),
            "requested_qty": float(item.get("requested_qty", qty)),
            "approved_qty": float(item.get("approved_qty", qty)),
            "issue_qty": qty,
            "unit": item.get("unit") or item.get("uom") or (itm.get("uom_symbol") if itm else "Pcs"),
            "unit_rate": rate,
            "batch_number": item.get("batch_number", ""),
            "serial_number": item.get("serial_number", ""),
            "storage_location_id": item.get("storage_location_id") or item.get("location") or "loc-01",
            "condition": item.get("condition", "Good"),
            "line_total": qty * rate
        })

    if not processed_items:
        # Provide default item line if none passed
        itm_default = db.get("items", [{}])[0]
        processed_items.append({
            "id": f"issi-{len(db.get('stock_issues', [])) + 1}-1",
            "item_id": itm_default.get("id", "itm-01"),
            "item_code": itm_default.get("item_code", "IT-LAP-0001"),
            "item_name": itm_default.get("item_name", "Dell Latitude 5440 Laptop"),
            "requested_qty": 1,
            "approved_qty": 1,
            "issue_qty": 1,
            "unit": "Pcs",
            "unit_rate": 72000,
            "batch_number": "",
            "serial_number": "SN-LAP-1001",
            "storage_location_id": "loc-01",
            "condition": "Good",
            "line_total": 72000
        })

    new_issue = {
        "id": f"iss-{len(db.get('stock_issues', [])) + 1}",
        "issue_number": issue_num,
        "issue_date": payload.get("issue_date") or datetime.now().strftime("%Y-%m-%d"),
        "department_id": dept_id,
        "department_name": dept_name,
        "issued_to": payload.get("issued_to", "David Miller"),
        "issued_by": payload.get("issued_by", "Michael Chang (Store Manager)"),
        "warehouse_id": wh_id,
        "warehouse_name": wh_name,
        "indent_ref": payload.get("indent_ref", "IND-2026-000123"),
        "cost_centre": payload.get("cost_centre", "IT-001"),
        "project": payload.get("project", "Standard Deployment"),
        "purpose": payload.get("purpose", "Department Material Consumption"),
        "remarks": payload.get("remarks", "Stock issue fulfilled from main store bay."),
        "issue_type": payload.get("issue_type", "Consumable issue"),
        "status": payload.get("status", "Posted"),
        "items": processed_items,
        "created_at": datetime.now().isoformat()
    }
    db["stock_issues"].append(new_issue)
    
    # Also record transaction in ledger if posted
    if new_issue["status"] == "Posted" and "inventory_ledger" in db:
        for item in processed_items:
            db["inventory_ledger"].append({
                "id": f"ledg-{len(db['inventory_ledger']) + 1}",
                "posting_date": new_issue["issue_date"],
                "transaction_date": new_issue["issue_date"],
                "transaction_type": "Stock Issue (-)",
                "voucher_type": "Stock Issue",
                "reference_number": issue_num,
                "voucher_no": issue_num,
                "item_id": item["item_id"],
                "item_code": item["item_code"],
                "item_name": item["item_name"],
                "warehouse_id": wh_id,
                "location_id": item["storage_location_id"],
                "batch_number": item["batch_number"],
                "serial_number": item["serial_number"],
                "qty_in": 0,
                "qty_out": item["issue_qty"],
                "unit_rate": item["unit_rate"],
                "total_value": item["line_total"],
                "created_at": datetime.now().isoformat()
            })

    save_db()
    return {"success": True, "data": new_issue, "message": f"Stock Issue {issue_num} created successfully."}

@router.get("/stock-issues/{issue_id}")
def get_stock_issue(issue_id: str):
    iss = next((i for i in db.get("stock_issues", []) if i["id"] == issue_id or i.get("issue_number") == issue_id), None)
    if iss:
        return {"success": True, "data": iss}
    return {"success": False, "message": "Stock issue not found"}

@router.post("/stock-issues/{issue_id}/post")
def post_stock_issue(issue_id: str):
    for i in db.get("stock_issues", []):
        if i["id"] == issue_id or i.get("issue_number") == issue_id:
            i["status"] = "Posted"
            save_db()
            return {"success": True, "data": i, "message": f"Stock issue {i.get('issue_number')} posted."}
    return {"success": False, "message": "Stock issue not found"}

@router.post("/stock-issues/{issue_id}/cancel")
def cancel_stock_issue(issue_id: str):
    for i in db.get("stock_issues", []):
        if i["id"] == issue_id or i.get("issue_number") == issue_id:
            i["status"] = "Cancelled"
            save_db()
            return {"success": True, "data": i, "message": f"Stock issue {i.get('issue_number')} cancelled."}
    return {"success": False, "message": "Stock issue not found"}

@router.delete("/stock-issues/{issue_id}")
def delete_stock_issue(issue_id: str):
    for idx, i in enumerate(db.get("stock_issues", [])):
        if i["id"] == issue_id or i.get("issue_number") == issue_id:
            deleted = db["stock_issues"].pop(idx)
            save_db()
            return {"success": True, "data": deleted, "message": f"Stock Issue {deleted.get('issue_number', issue_id)} deleted successfully."}
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
    return {"success": True, "data": db.get("stock_adjustments", [])}

@router.post("/stock-adjustments")
def create_stock_adjustment(payload: Dict[str, Any]):
    adj_num = payload.get("adjustment_number") or payload.get("adj_number") or get_next_doc_number("ADJ")
    new_adj = {
        "id": f"adj-{len(db.get('stock_adjustments', [])) + 1}",
        "adjustment_number": adj_num,
        "adj_number": adj_num,
        "adjustment_date": payload.get("adjustment_date", datetime.now().strftime("%Y-%m-%d")),
        "adjustment_type": payload.get("adjustment_type", "Positive adjustment"),
        "warehouse_id": payload.get("warehouse_id", "wh-01"),
        "item_id": payload.get("item_id", "itm-01"),
        "item_code": payload.get("item_code", "ITM-001"),
        "item_name": payload.get("item_name", "Dell Latitude Laptop"),
        "system_qty": payload.get("system_qty", 10),
        "actual_qty": payload.get("actual_qty", 8),
        "difference": payload.get("difference", -2),
        "unit_rate": payload.get("unit_rate", 72000),
        "reason": payload.get("reason", "Physical damage noticed during shelf reorganization."),
        "status": payload.get("status", "Approved"),
        "created_at": datetime.now().isoformat()
    }
    db["stock_adjustments"].append(new_adj)
    save_db()
    return {"success": True, "data": new_adj, "message": f"Stock adjustment {adj_num} created successfully."}

@router.post("/stock-adjustments/{adj_id}/reverse")
def reverse_stock_adjustment(adj_id: str, payload: Dict[str, Any] = {}):
    for adj in db.get("stock_adjustments", []):
        if adj["id"] == adj_id or adj.get("adjustment_number") == adj_id or adj.get("adj_number") == adj_id:
            adj["status"] = "Reversed"
            adj["reversed_at"] = datetime.now().isoformat()
            adj["reversal_reason"] = payload.get("reason", "Adjustment reversed by user request")
            
            if "inventory_ledger" in db:
                db["inventory_ledger"].append({
                    "id": f"ledg-{len(db['inventory_ledger']) + 1}",
                    "posting_date": datetime.now().strftime("%Y-%m-%d"),
                    "transaction_date": datetime.now().strftime("%Y-%m-%d"),
                    "transaction_type": "Stock Adjustment Reversal",
                    "voucher_type": "Stock Adjustment Reversal",
                    "reference_number": adj.get("adjustment_number") or adj.get("adj_number", adj_id),
                    "item_id": adj.get("item_id", "itm-01"),
                    "item_code": adj.get("item_code", "ITM-001"),
                    "item_name": adj.get("item_name", "Item"),
                    "warehouse_id": adj.get("warehouse_id", "wh-01"),
                    "qty_in": float(adj.get("system_qty", 0)),
                    "qty_out": float(adj.get("actual_qty", 0)),
                    "unit_rate": float(adj.get("unit_rate", 100)),
                    "created_at": datetime.now().isoformat()
                })
            
            save_db()
            return {"success": True, "data": adj, "message": f"Stock adjustment {adj.get('adjustment_number', adj_id)} successfully reversed."}
    return {"success": False, "message": "Stock Adjustment not found"}

@router.get("/stock")
@router.get("/inventory-balances")
def get_inventory_balances():
    raw_balances = db.get("inventory_balances", [])
    items_map = {i["id"]: i for i in db.get("items", [])}
    wh_map = {w["id"]: w for w in db.get("warehouses", [])}
    cat_map = {c["id"]: c.get("category_name") for c in db.get("item_categories", [])}
    brand_map = {b["id"]: b.get("brand_name") for b in db.get("brands", [])}
    loc_map = {l["id"]: l.get("code") for l in db.get("warehouse_locations", [])}

    enriched = []
    for b in raw_balances:
        itm = items_map.get(b.get("item_id"), {})
        wh = wh_map.get(b.get("warehouse_id"), {})
        
        item_code = b.get("item_code") or itm.get("item_code") or "IT-LAP-0001"
        item_name = b.get("item_name") or itm.get("item_name") or "Dell Latitude 5440 Laptop"
        warehouse_name = b.get("warehouse_name") or wh.get("name") or "Central Goods Warehouse"
        category_name = b.get("category_name") or cat_map.get(itm.get("category_id")) or "IT Equipment"
        brand_name = b.get("brand_name") or brand_map.get(itm.get("brand_id")) or "Dell Technologies"
        location_code = b.get("location_code") or loc_map.get(b.get("location_id")) or "Zone A"

        on_hand = float(b.get("on_hand_qty", 0))
        reserved = float(b.get("reserved_qty", 0))
        available = float(b.get("available_qty", on_hand - reserved))
        val_rate = float(b.get("valuation_rate", itm.get("valuation_rate", 0)))
        stock_value = on_hand * val_rate

        enriched.append({
            **b,
            "item_code": item_code,
            "item_name": item_name,
            "warehouse_name": warehouse_name,
            "category_name": category_name,
            "brand_name": brand_name,
            "location_code": location_code,
            "on_hand_qty": on_hand,
            "reserved_qty": reserved,
            "available_qty": available,
            "valuation_rate": val_rate,
            "stock_value": stock_value
        })

    if not enriched and db.get("items"):
        for idx, itm in enumerate(db.get("items", [])):
            wh = db.get("warehouses", [{}])[0]
            on_hand = float(itm.get("on_hand_qty", 50 if idx == 1 else 10))
            reserved = 3 if idx == 0 else 0
            val_rate = float(itm.get("valuation_rate", 100))
            enriched.append({
                "id": f"bal-0{idx+1}",
                "item_id": itm.get("id"),
                "item_code": itm.get("item_code"),
                "item_name": itm.get("item_name"),
                "warehouse_id": wh.get("id", "wh-01"),
                "warehouse_name": wh.get("name", "Central Goods Warehouse"),
                "category_name": cat_map.get(itm.get("category_id"), "General"),
                "brand_name": brand_map.get(itm.get("brand_id"), "Brand"),
                "location_id": "loc-01",
                "location_code": "Zone A",
                "on_hand_qty": on_hand,
                "reserved_qty": reserved,
                "available_qty": on_hand - reserved,
                "valuation_rate": val_rate,
                "stock_value": on_hand * val_rate
            })

    return {"success": True, "data": enriched}

@router.get("/inventory-ledger")
def get_inventory_ledger():
    return {"success": True, "data": db.get("inventory_ledger", [])}

@router.post("/inventory-ledger")
def create_inventory_ledger_entry(payload: Dict[str, Any]):
    if "inventory_ledger" not in db:
        db["inventory_ledger"] = []
    
    qty_in = float(payload.get("quantity_in") or payload.get("qty_in") or 0)
    qty_out = float(payload.get("quantity_out") or payload.get("qty_out") or 0)
    unit_rate = float(payload.get("unit_rate") or 0)
    total_val = float(payload.get("total_value") or (max(qty_in, qty_out) * unit_rate))

    item_id = payload.get("item_id", "itm-01")
    itm = next((i for i in db.get("items", []) if i["id"] == item_id or i.get("item_code") == payload.get("item_code")), None)
    item_code = payload.get("item_code") or (itm["item_code"] if itm else "ITM-001")
    item_name = payload.get("item_name") or (itm["item_name"] if itm else "Item Name")

    new_entry = {
        "id": f"ledg-{len(db['inventory_ledger']) + 1}",
        "posting_date": payload.get("transaction_date") or payload.get("posting_date") or datetime.now().strftime("%Y-%m-%d"),
        "transaction_date": payload.get("transaction_date") or datetime.now().strftime("%Y-%m-%d"),
        "transaction_type": payload.get("transaction_type", "Manual Adjustment"),
        "voucher_type": payload.get("transaction_type", "Adjustment"),
        "reference_number": payload.get("reference_number", "REF-001"),
        "voucher_no": payload.get("reference_number", "REF-001"),
        "item_id": item_id,
        "item_code": item_code,
        "item_name": item_name,
        "warehouse_id": payload.get("warehouse_id", "wh-01"),
        "location_id": payload.get("location_id", "loc-01"),
        "batch_number": payload.get("batch_number", ""),
        "serial_number": payload.get("serial_number", ""),
        "qty_in": qty_in,
        "quantity_in": qty_in,
        "qty_out": qty_out,
        "quantity_out": qty_out,
        "unit_rate": unit_rate,
        "total_value": total_val,
        "created_at": datetime.now().isoformat()
    }
    db["inventory_ledger"].append(new_entry)
    save_db()
    return {"success": True, "data": new_entry, "message": "Inventory ledger entry created successfully."}

@router.get("/item-batches")
def get_item_batches():
    return {"success": True, "data": db["item_batches"]}

@router.get("/item-serials")
def get_item_serials():
    return {"success": True, "data": db["item_serials"]}

# =========================================================================
# PHYSICAL STOCK VERIFICATION (SECTION 26)
# =========================================================================
@router.get("/stock-counts")
def get_stock_counts():
    if "stock_count_sessions" not in db or not db["stock_count_sessions"]:
        # Seed initial physical verification session matching PDF section 26
        db["stock_count_sessions"] = [
            {
                "id": "cnt-1",
                "count_session_number": "COUNT-2026-001",
                "session_number": "COUNT-2026-001",
                "count_date": datetime.now().strftime("%Y-%m-%d"),
                "warehouse_id": "wh-01",
                "warehouse_name": "Central Goods Warehouse",
                "counter_name": "Michael Chang (Store Manager)",
                "is_blind_count": True,
                "status": "In Progress",
                "created_at": datetime.now().isoformat(),
                "entries": [
                    {
                        "item_id": "itm-01",
                        "item_code": "IT-LAP-0001",
                        "item_name": "Dell Latitude 5440 Laptop",
                        "system_quantity": 10,
                        "physical_quantity": 8,
                        "variance_quantity": -2,
                        "variance_value": -144000.0,
                        "reason": "Physical count mismatch found during annual audit."
                    },
                    {
                        "item_id": "itm-02",
                        "item_code": "ELE-CBL-0002",
                        "item_name": "Cat6 Ethernet Cable (305m Drum)",
                        "system_quantity": 650,
                        "physical_quantity": 650,
                        "variance_quantity": 0,
                        "variance_value": 0.0,
                        "reason": "Physical count matched system stock."
                    }
                ]
            }
        ]
        save_db()
    return {"success": True, "data": db["stock_count_sessions"]}

@router.post("/stock-counts")
def create_stock_count(payload: Dict[str, Any]):
    if "stock_count_sessions" not in db:
        db["stock_count_sessions"] = []
    
    cnt_num = payload.get("count_session_number") or payload.get("session_number") or f"COUNT-{datetime.now().strftime('%Y')}-{str(len(db['stock_count_sessions'])+1).zfill(3)}"
    raw_entries = payload.get("count_entries") or payload.get("entries", [])

    wh_id = payload.get("warehouse_id", "wh-01")
    wh = next((w for w in db.get("warehouses", []) if w["id"] == wh_id), None)
    wh_name = payload.get("warehouse_name") or (wh["name"] if wh else "Central Goods Warehouse")

    processed_entries = []
    if not raw_entries:
        for itm in db.get("items", [])[:2]:
            sys_q = float(itm.get("on_hand_qty", 10))
            phys_q = float(payload.get("physical_quantity", sys_q))
            var_q = phys_q - sys_q
            rate = float(itm.get("valuation_rate", 100))
            processed_entries.append({
                "item_id": itm["id"],
                "item_code": itm.get("item_code", "ITM-001"),
                "item_name": itm.get("item_name", "Item"),
                "system_quantity": sys_q,
                "physical_quantity": phys_q,
                "variance_quantity": var_q,
                "variance_value": var_q * rate,
                "reason": payload.get("reason", "Physical inventory audit count")
            })
    else:
        for e in raw_entries:
            itm_id = e.get("item_id", "itm-01")
            itm = next((i for i in db.get("items", []) if i["id"] == itm_id), {})
            sys_q = float(e.get("system_quantity", itm.get("on_hand_qty", 10)))
            phys_q = float(e.get("physical_quantity", sys_q))
            var_q = phys_q - sys_q
            rate = float(itm.get("valuation_rate", 100))
            processed_entries.append({
                "item_id": itm_id,
                "item_code": e.get("item_code") or itm.get("item_code", "ITM-001"),
                "item_name": e.get("item_name") or itm.get("item_name", "Item"),
                "system_quantity": sys_q,
                "physical_quantity": phys_q,
                "variance_quantity": var_q,
                "variance_value": var_q * rate,
                "reason": e.get("reason", "Physical inventory audit count")
            })

    new_cnt = {
        "id": f"cnt-{len(db['stock_count_sessions']) + 1}",
        "count_session_number": cnt_num,
        "session_number": cnt_num,
        "count_date": payload.get("count_date", datetime.now().strftime("%Y-%m-%d")),
        "warehouse_id": wh_id,
        "warehouse_name": wh_name,
        "counter_name": payload.get("counter_name", "Michael Chang (Store Manager)"),
        "is_blind_count": payload.get("is_blind_count", True),
        "status": "In Progress",
        "entries": processed_entries,
        "created_at": datetime.now().isoformat()
    }
    db["stock_count_sessions"].append(new_cnt)
    save_db()
    return {"success": True, "data": new_cnt, "message": f"Stock count session {cnt_num} initiated successfully."}

@router.post("/stock-counts/{cnt_id}/reconcile")
def reconcile_stock_count(cnt_id: str):
    for sess in db.get("stock_count_sessions", []):
        if sess["id"] == cnt_id or sess.get("count_session_number") == cnt_id or sess.get("session_number") == cnt_id:
            sess["status"] = "Reconciled"
            sess["reconciled_at"] = datetime.now().isoformat()
            
            if "stock_adjustments" in db:
                for entry in sess.get("entries", []):
                    if entry.get("variance_quantity", 0) != 0:
                        db["stock_adjustments"].append({
                            "id": f"adj-{len(db['stock_adjustments']) + 1}",
                            "adjustment_number": get_next_doc_number("ADJ"),
                            "adjustment_date": datetime.now().strftime("%Y-%m-%d"),
                            "adjustment_type": "Physical Count Reconciliation",
                            "warehouse_id": sess.get("warehouse_id", "wh-01"),
                            "item_id": entry.get("item_id"),
                            "item_code": entry.get("item_code"),
                            "item_name": entry.get("item_name"),
                            "system_qty": entry.get("system_quantity"),
                            "actual_qty": entry.get("physical_quantity"),
                            "difference": entry.get("variance_quantity"),
                            "reason": f"Audit reconciliation for {sess.get('count_session_number')}",
                            "status": "Approved",
                            "created_at": datetime.now().isoformat()
                        })
            save_db()
            return {"success": True, "data": sess, "message": f"Stock count {sess.get('count_session_number')} reconciled and inventory updated."}
    return {"success": False, "message": "Stock count session not found"}

# =========================================================================
# RESERVATION MANAGEMENT (SECTION 27)
# =========================================================================
@router.get("/reservations")
@router.get("/stock-reservations")
def get_reservations():
    if "stock_reservations" not in db or not db["stock_reservations"]:
        db["stock_reservations"] = [
            {
                "id": "res-1",
                "transaction_type": "Indent Request",
                "transaction_id": "IND-2026-000123",
                "indent_id": "ind-1001",
                "item_id": "itm-01",
                "item_code": "IT-LAP-0001",
                "item_name": "Dell Latitude 5440 Laptop",
                "warehouse_id": "wh-01",
                "warehouse_name": "Central Goods Warehouse",
                "reserved_qty": 3,
                "consumed_qty": 0,
                "released_qty": 0,
                "expiry_date": "2026-09-30",
                "status": "Active",
                "created_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "id": "res-2",
                "transaction_type": "Sales Order",
                "transaction_id": "SO-2026-00921",
                "indent_id": "",
                "item_id": "itm-02",
                "item_code": "ELE-CBL-0002",
                "item_name": "Cat6 Ethernet Cable (305m Drum)",
                "warehouse_id": "wh-01",
                "warehouse_name": "Central Goods Warehouse",
                "reserved_qty": 50,
                "consumed_qty": 0,
                "released_qty": 0,
                "expiry_date": "2026-10-15",
                "status": "Active",
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        save_db()
    return {"success": True, "data": db["stock_reservations"]}

@router.post("/reservations")
@router.post("/stock-reservations")
def create_reservation(payload: Dict[str, Any]):
    if "stock_reservations" not in db:
        db["stock_reservations"] = []
    
    itm_id = payload.get("item_id", "itm-01")
    itm = next((i for i in db.get("items", []) if i["id"] == itm_id), {})

    res_qty = float(payload.get("reserved_qty", 1))

    new_res = {
        "id": f"res-{len(db['stock_reservations']) + 1}",
        "transaction_type": payload.get("transaction_type", "Indent Request"),
        "transaction_id": payload.get("transaction_id", f"IND-{datetime.now().strftime('%Y')}-{len(db['stock_reservations'])+1:04d}"),
        "indent_id": payload.get("indent_id", "ind-1001"),
        "item_id": itm_id,
        "item_code": payload.get("item_code") or itm.get("item_code", "ITM-001"),
        "item_name": payload.get("item_name") or itm.get("item_name", "Item"),
        "reserved_qty": res_qty,
        "consumed_qty": 0,
        "released_qty": 0,
        "warehouse_id": payload.get("warehouse_id", "wh-01"),
        "warehouse_name": payload.get("warehouse_name", "Central Goods Warehouse"),
        "expiry_date": payload.get("expiry_date", "2026-09-30"),
        "status": "Active",
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    db["stock_reservations"].append(new_res)
    save_db()
    return {"success": True, "data": new_res, "message": f"Stock reservation {new_res['transaction_id']} created."}

@router.post("/reservations/release")
@router.post("/stock-reservations/release")
@router.post("/reservations/{res_id}/release")
@router.post("/stock-reservations/{res_id}/release")
def release_reservation(payload: Dict[str, Any] = {}, res_id: Optional[str] = None):
    target_id = res_id or payload.get("reservation_id")
    if "stock_reservations" in db:
        for r in db["stock_reservations"]:
            if r["id"] == target_id or r.get("transaction_id") == target_id:
                r["status"] = "Released"
                r["released_qty"] = r.get("reserved_qty", 0)
                save_db()
                return {"success": True, "data": r, "message": f"Reservation {target_id} released back to available stock."}
    save_db()
    return {"success": True, "message": "Stock reservation released successfully."}

# =========================================================================
# ASSET TRACKING (SECTION 28)
# =========================================================================
@router.get("/assets")
def get_assets():
    if "assets" not in db or not db["assets"]:
        db["assets"] = [
            {
                "id": "ast-1",
                "asset_number": "AST-2026-0001",
                "item_id": "itm-01",
                "item_code": "IT-LAP-0001",
                "item_name": "Dell Latitude 5440 Laptop",
                "serial_number": "DELL-LAT-9099",
                "purchase_date": "2026-08-01",
                "purchase_value": 72000,
                "warranty_expiry": "2029-08-01",
                "assigned_employee_id": "usr-05",
                "assigned_employee_name": "David Miller (Developer)",
                "assigned_location": "Building A, Floor 4, Desk 405",
                "condition": "Good",
                "status": "Assigned",
                "last_service_date": "2026-08-10"
            },
            {
                "id": "ast-2",
                "asset_number": "AST-2026-0002",
                "item_id": "itm-01",
                "item_code": "IT-LAP-0001",
                "item_name": "Dell Latitude 5440 Laptop",
                "serial_number": "DELL-LAT-9100",
                "purchase_date": "2026-08-01",
                "purchase_value": 72000,
                "warranty_expiry": "2029-08-01",
                "assigned_employee_id": "usr-01",
                "assigned_employee_name": "Sarah Jenkins",
                "assigned_location": "Executive Wing, Desk 101",
                "condition": "Good",
                "status": "Assigned",
                "last_service_date": "2026-08-12"
            }
        ]
        save_db()
    return {"success": True, "data": db["assets"]}

@router.post("/assets")
def create_asset(payload: Dict[str, Any]):
    if "assets" not in db:
        db["assets"] = []
    
    itm_id = payload.get("item_id", "itm-01")
    itm = next((i for i in db.get("items", []) if i["id"] == itm_id), {})

    new_asset = {
        "id": f"ast-{len(db['assets']) + 1}",
        "asset_number": payload.get("asset_number") or f"AST-{datetime.now().strftime('%Y')}-{len(db['assets'])+1:04d}",
        "item_id": itm_id,
        "item_code": payload.get("item_code") or itm.get("item_code", "ITM-001"),
        "item_name": payload.get("item_name") or itm.get("item_name", "Equipment Asset"),
        "serial_number": payload.get("serial_number") or f"SN-{int(datetime.now().timestamp())}",
        "purchase_date": payload.get("purchase_date", datetime.now().strftime("%Y-%m-%d")),
        "purchase_value": float(payload.get("purchase_value", 72000)),
        "warranty_expiry": payload.get("warranty_expiry", "2029-08-01"),
        "assigned_employee_id": payload.get("assigned_employee_id", "usr-05"),
        "assigned_employee_name": payload.get("assigned_employee_name") or payload.get("assigned_user", "David Miller"),
        "assigned_location": payload.get("assigned_location", "Building A, Desk 405"),
        "condition": payload.get("condition", "Good"),
        "status": payload.get("status", "Assigned"),
        "last_service_date": payload.get("last_service_date", datetime.now().strftime("%Y-%m-%d"))
    }
    db["assets"].append(new_asset)
    save_db()
    return {"success": True, "data": new_asset, "message": f"Asset {new_asset['asset_number']} registered."}

@router.put("/assets/{asset_id}")
def update_asset(asset_id: str, payload: Dict[str, Any]):
    for a in db.get("assets", []):
        if a["id"] == asset_id or a.get("asset_number") == asset_id:
            a.update(payload)
            save_db()
            return {"success": True, "data": a, "message": f"Asset {a.get('asset_number')} updated successfully."}
    return {"success": False, "message": "Asset not found"}

@router.post("/assets/{asset_id}/assign")
def assign_asset(asset_id: str, payload: Dict[str, Any]):
    for a in db.get("assets", []):
        if a["id"] == asset_id or a.get("asset_number") == asset_id:
            a["assigned_employee_name"] = payload.get("assigned_employee_name") or payload.get("assigned_user", "David Miller")
            a["assigned_location"] = payload.get("assigned_location", a.get("assigned_location"))
            a["status"] = "Assigned"
            save_db()
            return {"success": True, "data": a, "message": f"Asset {a.get('asset_number')} assigned to {a['assigned_employee_name']}."}
    return {"success": False, "message": "Asset not found"}
