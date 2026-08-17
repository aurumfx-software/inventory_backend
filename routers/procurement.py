from fastapi import APIRouter
from db.database_store import db, save_db, get_next_doc_number
from schemas.schemas import POCreate
from datetime import datetime
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api", tags=["Procurement"])

# =========================================================================
# RFQ MANAGEMENT
# =========================================================================
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

@router.get("/rfqs/{rfq_id}")
def get_rfq(rfq_id: str):
    rfq = next((r for r in db["rfqs"] if r["id"] == rfq_id or r.get("rfq_number") == rfq_id), None)
    if rfq:
        return {"success": True, "data": rfq}
    return {"success": False, "message": "RFQ not found"}

@router.post("/rfqs/{rfq_id}/send")
def send_rfq(rfq_id: str):
    rfq = next((r for r in db["rfqs"] if r["id"] == rfq_id), None)
    if rfq:
        rfq["status"] = "Sent to Suppliers"
        save_db()
        return {"success": True, "message": f"RFQ {rfq_id} dispatched to suppliers."}
    return {"success": False, "message": "RFQ not found"}

@router.post("/rfqs/{rfq_id}/close")
def close_rfq(rfq_id: str):
    rfq = next((r for r in db["rfqs"] if r["id"] == rfq_id), None)
    if rfq:
        rfq["status"] = "Closed"
        save_db()
        return {"success": True, "message": f"RFQ {rfq_id} closed."}
    return {"success": False, "message": "RFQ not found"}

@router.get("/rfqs/{rfq_id}/supplier-status")
def get_rfq_supplier_status(rfq_id: str):
    return {"success": True, "data": [{"supplier_id": "sup-01", "status": "Responded"}, {"supplier_id": "sup-02", "status": "Pending"}]}

@router.get("/rfqs/{rfq_id}/comparison")
def get_rfq_comparison(rfq_id: str):
    return {"success": True, "data": db["quotations"]}

# =========================================================================
# QUOTATION MANAGEMENT
# =========================================================================
@router.get("/quotations")
def get_quotations():
    return {"success": True, "data": db["quotations"]}

@router.post("/quotations")
def create_quotation(payload: Dict[str, Any]):
    new_id = f"qte-{len(db['quotations']) + 1}"
    new_qte = {
        "id": new_id,
        "quotation_number": payload.get("quotation_number") or f"QTN-2026-0000{len(db['quotations'])+1}",
        "rfq_id": payload.get("rfq_id", "rfq-01"),
        "supplier_id": payload.get("supplier_id", "sup-01"),
        "supplier_name": payload.get("supplier_name", "Dell India Pvt Ltd"),
        "total_landed_cost": payload.get("total_landed_cost", 72000),
        "status": "Received",
        "created_at": datetime.now().isoformat()
    }
    db["quotations"].append(new_qte)
    save_db()
    return {"success": True, "data": new_qte}

@router.put("/quotations/{qte_id}")
def update_quotation(qte_id: str, payload: Dict[str, Any]):
    for q in db["quotations"]:
        if q["id"] == qte_id:
            q.update(payload)
            save_db()
            return {"success": True, "data": q}
    return {"success": False, "message": "Quotation not found"}

@router.post("/quotation-comparisons/{rfq_id}/select")
def select_winning_quotation(rfq_id: str, payload: Dict[str, Any]):
    return {"success": True, "message": f"Quotation selected successfully for RFQ {rfq_id}."}

# =========================================================================
# PURCHASE ORDER MANAGEMENT
# =========================================================================
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
        "status": "Draft",
        "total_amount": 1440000,
        "created_at": datetime.now().isoformat()
    }
    db["purchase_orders"].append(new_po)
    save_db()
    return {"success": True, "data": new_po}

@router.get("/purchase-orders/{po_id}")
def get_purchase_order(po_id: str):
    po = next((p for p in db["purchase_orders"] if p["id"] == po_id or p.get("po_number") == po_id), None)
    if po:
        return {"success": True, "data": po}
    return {"success": False, "message": "Purchase Order not found"}

@router.put("/purchase-orders/{po_id}")
def update_purchase_order(po_id: str, payload: Dict[str, Any]):
    for po in db["purchase_orders"]:
        if po["id"] == po_id:
            po.update(payload)
            save_db()
            return {"success": True, "data": po}
    return {"success": False, "message": "Purchase Order not found"}

@router.post("/purchase-orders/{po_id}/submit")
def submit_po(po_id: str):
    for po in db["purchase_orders"]:
        if po["id"] == po_id:
            po["status"] = "Pending approval"
            save_db()
            return {"success": True, "data": po}
    return {"success": False, "message": "Purchase Order not found"}

@router.post("/purchase-orders/{po_id}/approve")
def approve_po(po_id: str):
    for po in db["purchase_orders"]:
        if po["id"] == po_id:
            po["status"] = "Approved"
            save_db()
            return {"success": True, "data": po}
    return {"success": False, "message": "Purchase Order not found"}

@router.post("/purchase-orders/{po_id}/send")
def send_po(po_id: str):
    for po in db["purchase_orders"]:
        if po["id"] == po_id:
            po["status"] = "Sent to supplier"
            save_db()
            return {"success": True, "data": po}
    return {"success": False, "message": "Purchase Order not found"}

@router.post("/purchase-orders/{po_id}/accept")
def accept_po(po_id: str):
    for po in db["purchase_orders"]:
        if po["id"] == po_id:
            po["status"] = "Supplier accepted"
            save_db()
            return {"success": True, "data": po}
    return {"success": False, "message": "Purchase Order not found"}

@router.post("/purchase-orders/{po_id}/cancel")
def cancel_po(po_id: str):
    for po in db["purchase_orders"]:
        if po["id"] == po_id:
            po["status"] = "Cancelled"
            save_db()
            return {"success": True, "data": po}
    return {"success": False, "message": "Purchase Order not found"}

@router.get("/purchase-orders/{po_id}/pdf")
def get_po_pdf(po_id: str):
    po = next((p for p in db["purchase_orders"] if p["id"] == po_id), {})
    return {"success": True, "pdf_url": f"/docs/PO_{po.get('po_number', po_id)}.pdf"}

@router.get("/purchase-orders/{po_id}/pending-items")
def get_po_pending_items(po_id: str):
    return {"success": True, "data": db["items"][:2]}
