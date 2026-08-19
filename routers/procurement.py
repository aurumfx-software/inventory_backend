from fastapi import APIRouter
from db.database_store import db, save_db, get_next_doc_number
from schemas.schemas import POCreate
from datetime import datetime
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api", tags=["Procurement"])

INITIAL_RFQS = [
    {
        "id": "rfq-1",
        "rfq_number": "RFQ-2026-001001",
        "rfq_date": "2026-08-15",
        "due_date": "2026-08-30",
        "indent_id": "ind-1001",
        "indent_number": "IND-2026-001001",
        "buyer": "Sarah Jenkins (Buyer)",
        "delivery_location": "Central Goods Warehouse (WH-MAIN)",
        "currency": "INR",
        "terms": "Net 30 days, FOB Destination",
        "contact_person": "Vikram Malhotra",
        "status": "Published",
        "created_at": datetime.now().isoformat(),
        "items": [
            {
                "item_id": "itm-01",
                "item_code": "IT-LAP-0001",
                "item_name": "Dell Latitude 5440 Laptop",
                "specification": "Intel i7 13th Gen, 16GB RAM, 512GB SSD, 14-inch Display",
                "quantity": 20,
                "unit": "Pcs",
                "required_delivery_date": "2026-08-28"
            }
        ]
    },
    {
        "id": "rfq-2",
        "rfq_number": "RFQ-2026-002003",
        "rfq_date": "2026-08-18",
        "due_date": "2026-08-28",
        "indent_id": "ind-1001",
        "indent_number": "IND-2026-001001",
        "buyer": "Rajesh Kumar (Purchase Manager)",
        "delivery_location": "IT Store (WH-SUB1)",
        "currency": "INR",
        "terms": "Net 15 days",
        "contact_person": "Suresh Menon",
        "status": "Published",
        "created_at": datetime.now().isoformat(),
        "items": [
            {
                "item_id": "itm-02",
                "item_code": "ELE-CBL-0002",
                "item_name": "Cat6 Ethernet Cable (305m Drum)",
                "specification": "High speed Gigabit Shielded Copper Cable Drum",
                "quantity": 50,
                "unit": "Pcs",
                "required_delivery_date": "2026-08-28"
            }
        ]
    }
]

@router.get("/rfqs")
def get_rfqs():
    if not db.get("rfqs"):
        db["rfqs"] = INITIAL_RFQS
        save_db()
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
    if not db.get("rfqs"):
        db["rfqs"] = INITIAL_RFQS
        save_db()
    if not db.get("quotations"):
        db["quotations"] = INITIAL_QUOTATIONS
        save_db()

    rfq = next((r for r in db["rfqs"] if r["id"] == rfq_id or r.get("rfq_number") == rfq_id), db["rfqs"][0] if db["rfqs"] else None)

    if not rfq:
        rfq = {
            "id": rfq_id,
            "rfq_number": "RFQ-2026-001001",
            "closing_date": "2026-08-30",
            "due_date": "2026-08-30",
            "delivery_location": "Central Goods Warehouse (WH-MAIN)",
            "currency": "INR",
            "buyer": "Sarah Jenkins (Buyer)"
        }

    q_list = [q for q in db.get("quotations", []) if q.get("rfq_id") == rfq.get("id") or q.get("rfq_number") == rfq.get("rfq_number")]
    if not q_list:
        q_list = db.get("quotations", [])

    lowest_id = None
    if q_list:
        lowest_q = min(q_list, key=lambda x: float(x.get("total_landed_cost", 999999999)))
        lowest_id = lowest_q.get("id")

    return {
        "success": True,
        "rfq": {
            "id": rfq.get("id", rfq_id),
            "rfq_number": rfq.get("rfq_number", "RFQ-2026-001001"),
            "closing_date": rfq.get("due_date", rfq.get("closing_date", "2026-08-30")),
            "due_date": rfq.get("due_date", "2026-08-30"),
            "delivery_location": rfq.get("delivery_location", "Central Goods Warehouse"),
            "currency": rfq.get("currency", "INR"),
            "buyer": rfq.get("buyer", "Sarah Jenkins")
        },
        "quotations": q_list,
        "lowestCostQuoteId": lowest_id,
        "rfqItems": rfq.get("items", [
            {
                "item_id": "itm-01",
                "item_code": "IT-LAP-0001",
                "item_name": "Dell Latitude 5440 Laptop",
                "specification": "Intel i7 13th Gen, 16GB RAM",
                "quantity": 20,
                "unit": "Pcs",
                "previous_purchase_rate": 72000
            }
        ]),
        "selectionDecision": None
    }

# =========================================================================
# QUOTATION MANAGEMENT
# =========================================================================
INITIAL_QUOTATIONS = [
    {
        "id": "qte-01",
        "quotation_number": "QTN-2026-000001",
        "rfq_id": "rfq-1",
        "rfq_number": "RFQ-2026-001001",
        "supplier_id": "sup-01",
        "supplier_name": "Infotech Systems Ltd",
        "supplier_quotation_ref": "INF/QT/2026/88",
        "quotation_date": "2026-08-15",
        "valid_until_date": "2026-09-15",
        "currency": "INR",
        "payment_terms": "Net 30 days",
        "delivery_terms": "FOB Destination",
        "freight_terms": "Freight Prepaid",
        "warranty": "3 Years Onsite Warranty",
        "subtotal": 1220338.98,
        "tax_total": 219661.02,
        "total_landed_cost": 1440000,
        "status": "Approved",
        "is_selected": True,
        "items": [
            {
                "item_id": "itm-01",
                "item_code": "IT-LAP-0001",
                "item_name": "Dell Latitude 5440 Laptop",
                "offered_brand": "Dell Technologies",
                "offered_quantity": 20,
                "unit_rate": 72000,
                "discount_pct": 0,
                "tax_pct": 18,
                "line_total": 1440000,
                "delivery_days": 7
            }
        ]
    },
    {
        "id": "qte-02",
        "quotation_number": "QTN-2026-000002",
        "rfq_id": "rfq-1",
        "rfq_number": "RFQ-2026-001001",
        "supplier_id": "sup-02",
        "supplier_name": "Apex Electrical Controls",
        "supplier_quotation_ref": "AEC/QUOTE/55",
        "quotation_date": "2026-08-16",
        "valid_until_date": "2026-09-16",
        "currency": "INR",
        "payment_terms": "Net 15 days",
        "delivery_terms": "FOB Destination",
        "freight_terms": "Freight Prepaid",
        "warranty": "2 Years Standard",
        "subtotal": 1254237.29,
        "tax_total": 225762.71,
        "total_landed_cost": 1480000,
        "status": "Received",
        "is_selected": False,
        "items": [
            {
                "item_id": "itm-01",
                "item_code": "IT-LAP-0001",
                "item_name": "Dell Latitude 5440 Laptop",
                "offered_brand": "Dell Technologies",
                "offered_quantity": 20,
                "unit_rate": 74000,
                "discount_pct": 0,
                "tax_pct": 18,
                "line_total": 1480000,
                "delivery_days": 5
            }
        ]
    }
]

@router.get("/quotations")
def get_quotations():
    if not db.get("quotations"):
        db["quotations"] = INITIAL_QUOTATIONS
        save_db()
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
    return {"success": True, "data": db.get("purchase_orders", [])}

@router.post("/purchase-orders")
def create_purchase_order(payload: Dict[str, Any]):
    po_num = payload.get("po_number") or get_next_doc_number("PO")
    sup_id = payload.get("supplier_id", "")
    sup = next((s for s in db.get("suppliers", []) if s["id"] == sup_id), None)
    sup_name = payload.get("supplier_name") or (sup["supplier_name"] if sup else "")

    items = payload.get("items", [])
    processed_items = []
    subtotal = 0.0
    tax_total = 0.0

    for idx, item in enumerate(items):
        ord_qty = float(item.get("ordered_quantity", 1))
        unit_rate = float(item.get("unit_rate", 0))
        disc_pct = float(item.get("discount", 0))
        tax_pct = float(item.get("tax", 18))

        gross = ord_qty * unit_rate
        disc_val = (gross * disc_pct) / 100.0
        taxable = gross - disc_val
        tax_val = (taxable * tax_pct) / 100.0
        line_total = taxable + tax_val

        subtotal += taxable
        tax_total += tax_val

        processed_items.append({
            "po_item_id": f"poi-{len(db.get('purchase_orders', [])) + 1}-{idx + 1}",
            "item_id": item.get("item_id", ""),
            "item_code": item.get("item_code", "ITM-CODE"),
            "item_name": item.get("description_snapshot") or item.get("item_name", "Item"),
            "description_snapshot": item.get("description_snapshot", ""),
            "ordered_quantity": ord_qty,
            "received_quantity": float(item.get("received_quantity", 0)),
            "pending_quantity": float(item.get("pending_quantity", ord_qty)),
            "unit": item.get("unit", "Pcs"),
            "uom": item.get("unit", "Pcs"),
            "unit_rate": unit_rate,
            "discount": disc_pct,
            "tax": tax_pct,
            "line_total": line_total,
            "delivery_date": item.get("delivery_date", datetime.now().strftime("%Y-%m-%d")),
            "warehouse_id": item.get("warehouse_id", "wh-01")
        })

    grand_total = payload.get("grand_total") or (subtotal + tax_total) or payload.get("total_amount", 0)

    new_po = {
        "id": f"po-{len(db.get('purchase_orders', [])) + 1}",
        "po_number": po_num,
        "po_date": payload.get("po_date", datetime.now().strftime("%Y-%m-%d")),
        "supplier_id": sup_id,
        "supplier_name": sup_name,
        "supplier_address": payload.get("supplier_address") or (sup.get("address_registered") if sup else ""),
        "billing_address": payload.get("billing_address", "Apex Enterprises HQ, 100 Industrial Park, Zone 4, Bangalore"),
        "delivery_address": payload.get("delivery_address", "Central Goods Warehouse (WH-MAIN), Gate 2, Bangalore"),
        "currency": payload.get("currency", "INR"),
        "payment_terms": payload.get("payment_terms", "Net 30 days"),
        "delivery_terms": payload.get("delivery_terms", "FOB Destination"),
        "freight_terms": payload.get("freight_terms", "Freight Prepaid"),
        "buyer": payload.get("buyer", "Sarah Jenkins (Buyer)"),
        "quotation_id": payload.get("quotation_id", ""),
        "quotation_number": payload.get("quotation_number", ""),
        "rfq_id": payload.get("rfq_id", ""),
        "indent_id": payload.get("indent_id", ""),
        "terms_conditions": payload.get("terms_conditions", "Standard purchase terms apply."),
        "status": payload.get("status", "Draft"),
        "subtotal": subtotal,
        "tax_total": tax_total,
        "grand_total": grand_total,
        "total_amount": grand_total,
        "version_number": 1,
        "items": processed_items,
        "created_at": datetime.now().isoformat()
    }
    db["purchase_orders"].append(new_po)
    save_db()
    return {"success": True, "data": new_po, "message": f"Purchase Order {po_num} created successfully."}

@router.get("/purchase-orders/{po_id}")
def get_purchase_order(po_id: str):
    po = next((p for p in db.get("purchase_orders", []) if p["id"] == po_id or p.get("po_number") == po_id), None)
    if po:
        return {"success": True, "data": po}
    return {"success": False, "message": "Purchase Order not found"}

@router.put("/purchase-orders/{po_id}")
def update_purchase_order(po_id: str, payload: Dict[str, Any]):
    for po in db.get("purchase_orders", []):
        if po["id"] == po_id or po.get("po_number") == po_id:
            if po.get("status") == "Approved":
                po["version_number"] = po.get("version_number", 1) + 1
                po["status"] = "Pending approval"

            # If items provided, reprocess line totals
            if "items" in payload:
                processed_items = []
                subtotal = 0.0
                tax_total = 0.0
                for idx, item in enumerate(payload["items"]):
                    ord_qty = float(item.get("ordered_quantity", 1))
                    unit_rate = float(item.get("unit_rate", 0))
                    disc_pct = float(item.get("discount", 0))
                    tax_pct = float(item.get("tax", 18))
                    gross = ord_qty * unit_rate
                    disc_val = (gross * disc_pct) / 100.0
                    taxable = gross - disc_val
                    tax_val = (taxable * tax_pct) / 100.0
                    line_total = taxable + tax_val
                    subtotal += taxable
                    tax_total += tax_val

                    rec_qty = float(item.get("received_quantity", 0))
                    item["line_total"] = line_total
                    item["pending_quantity"] = max(0, ord_qty - rec_qty)
                    processed_items.append(item)
                
                payload["items"] = processed_items
                payload["subtotal"] = subtotal
                payload["tax_total"] = tax_total
                payload["grand_total"] = subtotal + tax_total
                payload["total_amount"] = subtotal + tax_total

            # Update supplier_name if supplier_id changed
            if "supplier_id" in payload:
                sup = next((s for s in db.get("suppliers", []) if s["id"] == payload["supplier_id"]), None)
                if sup:
                    payload["supplier_name"] = sup.get("supplier_name", po.get("supplier_name"))

            po.update(payload)
            save_db()
            return {"success": True, "data": po, "message": f"Purchase Order {po.get('po_number')} updated successfully."}
    return {"success": False, "message": "Purchase Order not found"}

@router.post("/purchase-orders/{po_id}/submit")
def submit_po(po_id: str):
    for po in db.get("purchase_orders", []):
        if po["id"] == po_id or po.get("po_number") == po_id:
            po["status"] = "Pending approval"
            save_db()
            return {"success": True, "data": po, "message": f"PO {po.get('po_number')} submitted for approval."}
    return {"success": False, "message": "Purchase Order not found"}

@router.post("/purchase-orders/{po_id}/approve")
def approve_po(po_id: str):
    for po in db.get("purchase_orders", []):
        if po["id"] == po_id or po.get("po_number") == po_id:
            po["status"] = "Approved"
            save_db()
            return {"success": True, "data": po, "message": f"PO {po.get('po_number')} approved successfully."}
    return {"success": False, "message": "Purchase Order not found"}

@router.post("/purchase-orders/{po_id}/send")
def send_po(po_id: str):
    for po in db.get("purchase_orders", []):
        if po["id"] == po_id or po.get("po_number") == po_id:
            po["status"] = "Sent to supplier"
            save_db()
            return {"success": True, "data": po, "message": f"PO {po.get('po_number')} sent to supplier."}
    return {"success": False, "message": "Purchase Order not found"}

@router.post("/purchase-orders/{po_id}/accept")
def accept_po(po_id: str):
    for po in db.get("purchase_orders", []):
        if po["id"] == po_id or po.get("po_number") == po_id:
            po["status"] = "Supplier accepted"
            save_db()
            return {"success": True, "data": po, "message": f"PO {po.get('po_number')} accepted by supplier."}
    return {"success": False, "message": "Purchase Order not found"}

@router.post("/purchase-orders/{po_id}/cancel")
def cancel_po(po_id: str, payload: Dict[str, Any] = None):
    for po in db.get("purchase_orders", []):
        if po["id"] == po_id or po.get("po_number") == po_id:
            po["status"] = "Cancelled"
            if payload and "reason" in payload:
                po["cancel_reason"] = payload["reason"]
            save_db()
            return {"success": True, "data": po, "message": f"PO {po.get('po_number')} cancelled."}
    return {"success": False, "message": "Purchase Order not found"}

@router.get("/purchase-orders/{po_id}/pdf")
def get_po_pdf(po_id: str):
    po = next((p for p in db.get("purchase_orders", []) if p["id"] == po_id or p.get("po_number") == po_id), {})
    return {"success": True, "pdf_url": f"/docs/PO_{po.get('po_number', po_id)}.pdf"}

@router.get("/purchase-orders/{po_id}/pending-items")
def get_po_pending_items(po_id: str):
    po = next((p for p in db.get("purchase_orders", []) if p["id"] == po_id or p.get("po_number") == po_id), None)
    if not po:
        return {"success": False, "message": "Purchase Order not found"}
    
    sup_id = po.get("supplier_id")
    sup = next((s for s in db.get("suppliers", []) if s["id"] == sup_id), None)
    sup_name = po.get("supplier_name") or (sup["supplier_name"] if sup else "Supplier Name")

    po_info = {
        "id": po["id"],
        "po_number": po.get("po_number"),
        "supplier_id": sup_id or (sup["id"] if sup else "sup-01"),
        "supplier_name": sup_name,
        "warehouse_id": po.get("warehouse_id", "wh-01")
    }

    raw_items = po.get("items", [])
    if not raw_items:
        items_master = db.get("items", [])[:2]
        raw_items = [
            {
                "po_item_id": f"poi-{idx+1}",
                "item_id": itm.get("id"),
                "item_code": itm.get("item_code", f"ITM-00{idx+1}"),
                "item_name": itm.get("item_name", "Item Name"),
                "uom": itm.get("uom_symbol", "Pcs"),
                "ordered_quantity": 20,
                "previously_received_qty": 0,
                "pending_quantity": 20,
                "is_batch_tracked": itm.get("is_batch_tracked", False),
                "is_serial_tracked": itm.get("is_serial_tracked", False),
                "is_expiry_tracked": itm.get("is_expiry_tracked", False),
                "unit_rate": itm.get("valuation_rate", 72000)
            }
            for idx, itm in enumerate(items_master)
        ]

    pending_items = []
    for idx, pi in enumerate(raw_items):
        ord_qty = float(pi.get("ordered_quantity", pi.get("ordered_qty", 20)))
        prev_rec = float(pi.get("previously_received_qty", pi.get("received_quantity", 0)))
        pend_qty = float(pi.get("pending_quantity", max(0, ord_qty - prev_rec)))

        itm_id = pi.get("item_id")
        itm_master = next((i for i in db.get("items", []) if i["id"] == itm_id), {})

        pending_items.append({
            "po_item_id": pi.get("po_item_id", f"poi-{idx+1}"),
            "item_id": itm_id or f"itm-0{idx+1}",
            "item_code": pi.get("item_code") or itm_master.get("item_code", "ITM-CODE"),
            "item_name": pi.get("item_name") or pi.get("description_snapshot") or itm_master.get("item_name", "Item Name"),
            "uom": pi.get("unit") or pi.get("uom") or itm_master.get("uom_symbol", "Pcs"),
            "ordered_qty": ord_qty,
            "ordered_quantity": ord_qty,
            "previously_received_qty": prev_rec,
            "pending_quantity": pend_qty,
            "is_batch_tracked": pi.get("is_batch_tracked", itm_master.get("is_batch_tracked", False)),
            "is_serial_tracked": pi.get("is_serial_tracked", itm_master.get("is_serial_tracked", False)),
            "is_expiry_tracked": pi.get("is_expiry_tracked", itm_master.get("is_expiry_tracked", False)),
            "unit_rate": pi.get("unit_rate", 72000)
        })

    return {"success": True, "data": {"po": po_info, "items": pending_items}}

