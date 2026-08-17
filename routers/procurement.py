from fastapi import APIRouter
from db.database_store import db, save_db, get_next_doc_number
from schemas.schemas import POCreate
from datetime import datetime
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["Procurement"])

@router.get("/rfqs")
def get_rfqs():
    return {"success": True, "data": db["rfqs"]}

@router.post("/rfqs")
def create_rfq(payload: Dict[str, Any]):
    rfq_num = get_next_doc_number("RFQ")
    new_rfq = {
        "id": f"rfq-{len(db['rfqs']) + 1}",
        "rfq_number": rfq_num,
        "rfq_date": datetime.now().strftime("%Y-%m-%d"),
        "indent_id": payload.get("indent_id", "ind-1001"),
        "status": "Published",
        "due_date": payload.get("due_date", "2026-08-28"),
        "created_at": datetime.now().isoformat()
    }
    db["rfqs"].append(new_rfq)
    save_db()
    return {"success": True, "data": new_rfq}

@router.get("/quotations")
def get_quotations():
    return {"success": True, "data": db["quotations"]}

@router.get("/purchase-orders")
def get_purchase_orders():
    return {"success": True, "data": db["purchase_orders"]}

@router.post("/purchase-orders")
def create_purchase_order(po: POCreate):
    po_num = get_next_doc_number("PO")
    new_po = {
        "id": f"po-{len(db['purchase_orders']) + 1}",
        "po_number": po_num,
        "po_date": po.po_date or datetime.now().strftime("%Y-%m-%d"),
        "supplier_id": po.supplier_id,
        "payment_terms": po.payment_terms or "Net 30 days",
        "delivery_date": po.delivery_date or "2026-08-30",
        "status": "Approved",
        "total_amount": 1440000,
        "created_at": datetime.now().isoformat()
    }
    db["purchase_orders"].append(new_po)
    save_db()
    return {"success": True, "data": new_po}
