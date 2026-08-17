from fastapi import APIRouter
from db.database_store import db, save_db, get_next_doc_number
from schemas.schemas import GRNCreate
from datetime import datetime
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["Inventory Operations"])

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

@router.get("/quality-inspections")
def get_quality_inspections():
    return {"success": True, "data": db["quality_inspections"]}

@router.get("/stock-issues")
def get_stock_issues():
    return {"success": True, "data": db["stock_issues"]}

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

@router.get("/stock-returns")
def get_stock_returns():
    return {"success": True, "data": db["stock_returns"]}

@router.get("/supplier-returns")
def get_supplier_returns():
    return {"success": True, "data": db["supplier_returns"]}

@router.get("/stock-adjustments")
def get_stock_adjustments():
    return {"success": True, "data": db["stock_adjustments"]}

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

@router.get("/assets")
def get_assets():
    return {"success": True, "data": db["assets"]}
