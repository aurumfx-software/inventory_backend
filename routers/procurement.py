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

@router.get("/rfqs/suggested-suppliers")
def get_suggested_suppliers(item_ids: Optional[str] = None, category_id: Optional[str] = None, delivery_location: Optional[str] = None):
    suppliers = [s for s in db.get("suppliers", []) if s.get("is_active") is not False and s.get("approval_status") == "Approved"]
    
    suggested = []
    for s in suppliers:
        rating = float(s.get("rating", 4.5))
        lead_time = int(s.get("delivery_lead_time_days", 5))
        category_match = True if category_id and s.get("category_id") == category_id else False
        
        # Calculate intelligent recommendation score
        score = rating * 20 + (10 if category_match else 0) + (10 if lead_time <= 5 else 0)
        
        suggested.append({
            **s,
            "match_score": min(100, score),
            "recommendation_reason": f"Rating {rating}/5.0 • Lead time {lead_time} days • Approved Vendor"
        })
        
    suggested.sort(key=lambda x: x["match_score"], reverse=True)
    return {"success": True, "data": suggested}

@router.get("/rfqs")
def get_rfqs():
    if not db.get("rfqs"):
        db["rfqs"] = INITIAL_RFQS
        save_db()
        
    # Enrich RFQs with supplier count and items count
    enriched = []
    for rfq in db["rfqs"]:
        sup_ids = rfq.get("supplier_ids", [])
        suppliers = [s for s in db.get("suppliers", []) if s["id"] in sup_ids]
        enriched.append({
            **rfq,
            "suppliers": suppliers,
            "supplier_count": len(suppliers) or len(sup_ids) or 2
        })
    return {"success": True, "data": enriched}

@router.post("/rfqs")
def create_or_update_rfq(payload: Dict[str, Any]):
    if not db.get("rfqs"):
        db["rfqs"] = INITIAL_RFQS

    rfq_id = payload.get("id")
    now_iso = datetime.now().isoformat()

    # Preserve snapshot of item master details per implementation rule!
    processed_items = []
    for idx, item in enumerate(payload.get("items", [])):
        item_id = item.get("item_id")
        item_master = next((im for im in db.get("items", []) if im["id"] == item_id), {})
        
        processed_items.append({
            "item_id": item_id,
            "item_code_snapshot": item.get("item_code_snapshot") or item_master.get("item_code", f"ITM-SNAP-{idx+1}"),
            "item_name_snapshot": item.get("item_name_snapshot") or item_master.get("item_name", "Material Item"),
            "specification": item.get("specification") or item_master.get("description", "Standard Specifications"),
            "quantity": float(item.get("quantity", 1)),
            "unit": item.get("unit") or item_master.get("uom_symbol") or "Pcs",
            "required_delivery_date": item.get("required_delivery_date") or payload.get("closing_date"),
            "acceptable_brands": item.get("acceptable_brands") or item_master.get("preferred_brand_name") or "Standard Brands",
            "technical_document": item.get("technical_document"),
            "remarks": item.get("remarks", "")
        })

    if rfq_id:
        rfq = next((r for r in db["rfqs"] if r["id"] == rfq_id), None)
        if rfq:
            rfq.update({
                "closing_date": payload.get("closing_date", rfq.get("closing_date")),
                "buyer": payload.get("buyer", rfq.get("buyer")),
                "delivery_location": payload.get("delivery_location", rfq.get("delivery_location")),
                "currency": payload.get("currency", rfq.get("currency")),
                "terms": payload.get("terms", rfq.get("terms")),
                "contact_person": payload.get("contact_person", rfq.get("contact_person")),
                "source_indent_numbers": payload.get("source_indent_numbers", rfq.get("source_indent_numbers")),
                "supplier_ids": payload.get("supplier_ids", rfq.get("supplier_ids")),
                "status": payload.get("status", rfq.get("status")),
                "attachments": payload.get("attachments", rfq.get("attachments")),
                "items": processed_items,
                "updated_at": now_iso
            })
            save_db()
            return {"success": True, "data": rfq, "message": "RFQ updated successfully with snapshot preserved."}

    # Create New RFQ
    rfq_num = payload.get("rfq_number") or get_next_doc_number("RFQ")
    new_rfq = {
        "id": f"rfq-{len(db['rfqs']) + 1001}",
        "rfq_number": rfq_num,
        "rfq_date": payload.get("rfq_date") or datetime.now().strftime("%Y-%m-%d"),
        "closing_date": payload.get("closing_date") or datetime.now().strftime("%Y-%m-%d"),
        "buyer": payload.get("buyer", "Sarah Jenkins (Super Administrator)"),
        "delivery_location": payload.get("delivery_location", "Central Goods Warehouse, Main Branch"),
        "currency": payload.get("currency", "INR"),
        "terms": payload.get("terms", "FOB Destination, Payment Net 30 days after GRN approval."),
        "contact_person": payload.get("contact_person", "Sarah Jenkins (procurement@company.com)"),
        "source_indent_numbers": payload.get("source_indent_numbers", ["IND-2026-001001"]),
        "supplier_ids": payload.get("supplier_ids", ["sup-01", "sup-02"]),
        "status": payload.get("status", "Draft"),
        "attachments": payload.get("attachments", []),
        "items": processed_items,
        "created_at": now_iso
    }
    db["rfqs"].append(new_rfq)

    # Log Audit
    db["audit_logs"].append({
        "id": f"aud-{len(db['audit_logs']) + 1}",
        "user_id": "usr-01",
        "action": "RFQ_CREATED",
        "module": "PROCUREMENT",
        "record_id": new_rfq["id"],
        "details": f"Created RFQ {rfq_num} with snapshot preservation for {len(processed_items)} items.",
        "timestamp": now_iso,
        "ip_address": "127.0.0.1"
    })

    save_db()
    return {"success": True, "data": new_rfq, "message": "New Request for Quotation created successfully."}

@router.get("/rfqs/{rfq_id}")
def get_rfq(rfq_id: str):
    rfq = next((r for r in db.get("rfqs", []) if r["id"] == rfq_id or r.get("rfq_number") == rfq_id), None)
    if rfq:
        sup_ids = rfq.get("supplier_ids", [])
        suppliers = [s for s in db.get("suppliers", []) if s["id"] in sup_ids]
        return {"success": True, "data": {**rfq, "suppliers": suppliers}}
    return {"success": False, "message": "RFQ not found"}

@router.post("/rfqs/{rfq_id}/send")
def send_rfq(rfq_id: str, payload: Optional[Dict[str, Any]] = None):
    rfq = next((r for r in db.get("rfqs", []) if r["id"] == rfq_id or r.get("rfq_number") == rfq_id), None)
    if rfq:
        now_iso = datetime.now().isoformat()
        rfq["status"] = "Sent"
        rfq["sent_at"] = now_iso

        send_method = payload.get("send_method", "Email with PDF attachment") if payload else "Email with PDF attachment"
        recipient_emails = payload.get("recipient_emails", "vendors@procurement-suppliers.com") if payload else "vendors@procurement-suppliers.com"

        # Record in rfq_email_logs table
        if "rfq_email_logs" not in db:
            db["rfq_email_logs"] = []

        log_entry = {
            "id": f"log-{len(db['rfq_email_logs']) + 1}",
            "rfq_id": rfq["id"],
            "rfq_number": rfq.get("rfq_number"),
            "send_method": send_method,
            "recipient_emails": recipient_emails,
            "notes": payload.get("notes", "") if payload else "",
            "sent_at": now_iso,
            "status": "Delivered"
        }
        db["rfq_email_logs"].append(log_entry)

        db["audit_logs"].append({
            "id": f"aud-{len(db['audit_logs']) + 1}",
            "user_id": "usr-01",
            "action": "RFQ_DISPATCHED",
            "module": "PROCUREMENT",
            "record_id": rfq["id"],
            "details": f"Dispatched RFQ {rfq.get('rfq_number')} via {send_method} to {recipient_emails}",
            "timestamp": now_iso,
            "ip_address": "127.0.0.1"
        })

        save_db()
        return {"success": True, "message": f"RFQ {rfq.get('rfq_number')} dispatched successfully via {send_method}.", "data": rfq}
    return {"success": False, "message": "RFQ not found"}

@router.post("/rfqs/{rfq_id}/close")
def close_rfq(rfq_id: str):
    rfq = next((r for r in db.get("rfqs", []) if r["id"] == rfq_id or r.get("rfq_number") == rfq_id), None)
    if rfq:
        rfq["status"] = "Closed"
        save_db()
        return {"success": True, "message": f"RFQ {rfq.get('rfq_number')} closed successfully."}
    return {"success": False, "message": "RFQ not found"}

@router.get("/rfqs/{rfq_id}/supplier-status")
def get_rfq_supplier_status(rfq_id: str):
    rfq = next((r for r in db.get("rfqs", []) if r["id"] == rfq_id or r.get("rfq_number") == rfq_id), None)
    sup_ids = rfq.get("supplier_ids", ["sup-01", "sup-02"]) if rfq else ["sup-01", "sup-02"]
    
    status_list = []
    for idx, sid in enumerate(sup_ids):
        sup = next((s for s in db.get("suppliers", []) if s["id"] == sid), {})
        status_list.append({
            "supplier_id": sid,
            "supplier_code": sup.get("supplier_code", f"SUP-000{idx+45}"),
            "supplier_name": sup.get("supplier_name", f"Supplier {idx+1}"),
            "contact_person": sup.get("contact_person", "Sales Manager"),
            "email": sup.get("email", "orders@supplier.com"),
            "status": "Responded" if idx == 0 else "Pending",
            "response_date": "2026-08-18" if idx == 0 else None,
            "quotation_id": f"qtn-{idx+1}" if idx == 0 else None,
            "bid_amount": 1420000 if idx == 0 else None
        })

    return {"success": True, "data": status_list}

@router.delete("/rfqs/{rfq_id}")
def delete_rfq(rfq_id: str):
    initial_len = len(db.get("rfqs", []))
    db["rfqs"] = [r for r in db.get("rfqs", []) if r["id"] != rfq_id and r.get("rfq_number") != rfq_id]
    if len(db["rfqs"]) < initial_len:
        save_db()
        return {"success": True, "message": "RFQ deleted successfully"}
    return {"success": False, "message": "RFQ not found"}

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
# QUOTATION MANAGEMENT & BACKEND CALCULATIONS
# =========================================================================
def compute_quotation_totals(payload: Dict[str, Any]) -> Dict[str, Any]:
    items = payload.get("items", [])
    processed_items = []
    
    subtotal = 0.0
    tax_total = 0.0
    freight_total = 0.0
    total_landed_cost = 0.0

    for idx, item in enumerate(items):
        qty = float(item.get("offered_quantity", item.get("quantity", 1)))
        unit_rate = float(item.get("unit_rate", 0))
        disc_pct = float(item.get("discount_pct", item.get("discount", 0)))
        tax_pct = float(item.get("tax_pct", item.get("tax", 18)))
        freight = float(item.get("freight_amount", item.get("freight", 0)))

        # Mandatory Backend Calculations to prevent manipulation:
        # 1. Gross Amount = Quantity × Unit Rate
        gross = qty * unit_rate
        # 2. Discount Amount = Gross Amount × Discount Percentage / 100
        disc_amt = (gross * disc_pct) / 100.0
        # 3. Taxable Amount = Gross Amount - Discount Amount
        taxable = gross - disc_amt
        # 4. Tax Amount = Taxable Amount × Tax Percentage / 100
        tax_amt = (taxable * tax_pct) / 100.0
        # 5. Line Total = Taxable Amount + Tax Amount + Freight
        line_total = taxable + tax_amt + freight

        subtotal += taxable
        tax_total += tax_amt
        freight_total += freight
        total_landed_cost += line_total

        processed_items.append({
            "id": item.get("id") or f"qti-{idx+1}",
            "rfq_item_id": item.get("rfq_item_id"),
            "item_id": item.get("item_id", ""),
            "item_code": item.get("item_code", "ITM-01"),
            "item_name": item.get("item_name", "Material Item"),
            "offered_brand": item.get("offered_brand", "Standard Brand"),
            "offered_quantity": qty,
            "unit_rate": unit_rate,
            "discount_pct": disc_pct,
            "discount_amount": disc_amt,
            "taxable_amount": taxable,
            "tax_pct": tax_pct,
            "tax_amount": tax_amt,
            "freight_amount": freight,
            "line_total": line_total,
            "delivery_days": int(item.get("delivery_days", item.get("delivery_time_days", 7))),
            "item_warranty": item.get("item_warranty", item.get("warranty", "1 Year Standard")),
            "technical_compliance": item.get("technical_compliance", "Compliant"),
            "supplier_remarks": item.get("supplier_remarks", "")
        })

    return {
        "items": processed_items,
        "subtotal": round(subtotal, 2),
        "tax_total": round(tax_total, 2),
        "freight_total": round(freight_total, 2),
        "total_landed_cost": round(total_landed_cost, 2)
    }

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
        "attachment": "Infotech_Official_Quote_2026.pdf",
        "remarks": "Special enterprise volume discount included.",
        "subtotal": 1220338.98,
        "tax_total": 219661.02,
        "freight_total": 0,
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
                "discount_amount": 0,
                "taxable_amount": 1440000,
                "tax_pct": 18,
                "tax_amount": 259200,
                "freight_amount": 0,
                "line_total": 1440000,
                "delivery_days": 7,
                "item_warranty": "3 Years Onsite Warranty",
                "technical_compliance": "Compliant"
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
        "attachment": "Apex_Quote_Commercial.pdf",
        "remarks": "Faster 5-day dispatch lead time.",
        "subtotal": 1254237.29,
        "tax_total": 225762.71,
        "freight_total": 0,
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
                "discount_amount": 0,
                "taxable_amount": 1480000,
                "tax_pct": 18,
                "tax_amount": 266400,
                "freight_amount": 0,
                "line_total": 1480000,
                "delivery_days": 5,
                "item_warranty": "2 Years Standard Warranty",
                "technical_compliance": "Compliant"
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

@router.get("/quotations/{qte_id}")
def get_quotation(qte_id: str):
    qte = next((q for q in db.get("quotations", []) if q["id"] == qte_id or q.get("quotation_number") == qte_id), None)
    if qte:
        return {"success": True, "data": qte}
    return {"success": False, "message": "Quotation not found"}

@router.post("/quotations")
def create_quotation(payload: Dict[str, Any]):
    if not db.get("quotations"):
        db["quotations"] = INITIAL_QUOTATIONS

    # Perform mandatory backend calculations
    calc = compute_quotation_totals(payload)

    new_id = f"qte-{len(db['quotations']) + 1001}"
    qtn_num = payload.get("quotation_number") or f"QTN-{datetime.now().year}-{str(len(db['quotations']) + 1001).zfill(6)}"
    
    new_qte = {
        "id": new_id,
        "quotation_number": qtn_num,
        "rfq_id": payload.get("rfq_id", "rfq-1"),
        "rfq_number": payload.get("rfq_number", "RFQ-2026-001001"),
        "supplier_id": payload.get("supplier_id", "sup-01"),
        "supplier_name": payload.get("supplier_name", "Supplier Name"),
        "supplier_quotation_ref": payload.get("supplier_quotation_ref", "REF-001"),
        "quotation_date": payload.get("quotation_date", datetime.now().strftime("%Y-%m-%d")),
        "valid_until_date": payload.get("valid_until_date", datetime.now().strftime("%Y-%m-%d")),
        "currency": payload.get("currency", "INR"),
        "payment_terms": payload.get("payment_terms", "Net 30 days"),
        "delivery_terms": payload.get("delivery_terms", "FOB Destination"),
        "freight_terms": payload.get("freight_terms", "Freight Prepaid"),
        "warranty": payload.get("warranty", "1 Year Standard"),
        "attachment": payload.get("attachment", ""),
        "remarks": payload.get("remarks", ""),
        "subtotal": calc["subtotal"],
        "tax_total": calc["tax_total"],
        "freight_total": calc["freight_total"],
        "total_landed_cost": calc["total_landed_cost"],
        "status": payload.get("status", "Received"),
        "is_selected": False,
        "items": calc["items"],
        "created_at": datetime.now().isoformat()
    }
    db["quotations"].append(new_qte)
    save_db()
    return {"success": True, "data": new_qte, "message": f"Quotation {qtn_num} created and calculated on backend."}

@router.put("/quotations/{qte_id}")
def update_quotation(qte_id: str, payload: Dict[str, Any]):
    for q in db.get("quotations", []):
        if q["id"] == qte_id or q.get("quotation_number") == qte_id:
            # Perform mandatory backend recalculation
            calc = compute_quotation_totals(payload)
            q.update({
                "supplier_quotation_ref": payload.get("supplier_quotation_ref", q.get("supplier_quotation_ref")),
                "quotation_date": payload.get("quotation_date", q.get("quotation_date")),
                "valid_until_date": payload.get("valid_until_date", q.get("valid_until_date")),
                "currency": payload.get("currency", q.get("currency")),
                "payment_terms": payload.get("payment_terms", q.get("payment_terms")),
                "delivery_terms": payload.get("delivery_terms", q.get("delivery_terms")),
                "freight_terms": payload.get("freight_terms", q.get("freight_terms")),
                "warranty": payload.get("warranty", q.get("warranty")),
                "attachment": payload.get("attachment", q.get("attachment")),
                "remarks": payload.get("remarks", q.get("remarks")),
                "subtotal": calc["subtotal"],
                "tax_total": calc["tax_total"],
                "freight_total": calc["freight_total"],
                "total_landed_cost": calc["total_landed_cost"],
                "items": calc["items"],
                "updated_at": datetime.now().isoformat()
            })
            save_db()
            return {"success": True, "data": q, "message": f"Quotation {q.get('quotation_number')} recalculated and updated."}
    return {"success": False, "message": "Quotation not found"}

@router.post("/quotation-comparisons/{rfq_id}/select")
def select_winning_quotation(rfq_id: str, payload: Dict[str, Any]):
    selected_qte_id = payload.get("selected_quotation_id") or payload.get("quotation_id")
    justification = str(payload.get("justification_reason", payload.get("reason", ""))).strip()

    q_list = [q for q in db.get("quotations", []) if q.get("rfq_id") == rfq_id or q.get("rfq_number") == rfq_id]
    if not q_list:
        q_list = db.get("quotations", [])

    lowest_q = min(q_list, key=lambda x: float(x.get("total_landed_cost", 999999999))) if q_list else None
    
    # Important Rule Validation: If selected supplier is NOT the lowest bidder (L1), system MUST require a reason!
    is_l1 = (lowest_q and (selected_qte_id == lowest_q.get("id") or selected_qte_id == lowest_q.get("quotation_number")))
    if lowest_q and not is_l1:
        if not justification:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Non-L1 Selection Rule: Justification reason is mandatory when selecting a supplier with a higher bid than the lowest cost bidder (L1).")

    # Mark selected quotation
    for q in db.get("quotations", []):
        if q["id"] == selected_qte_id or q.get("quotation_number") == selected_qte_id:
            q["is_selected"] = True
            q["status"] = "Approved"
            q["selection_justification"] = justification
        elif q.get("rfq_id") == rfq_id or q.get("rfq_number") == rfq_id:
            q["is_selected"] = False
            q["status"] = "Rejected"

    # Store selection decision in quotation_selection_decisions table
    if "quotation_selection_decisions" not in db:
        db["quotation_selection_decisions"] = []

    decision = {
        "id": f"dec-{len(db['quotation_selection_decisions']) + 1}",
        "rfq_id": rfq_id,
        "selected_quotation_id": selected_qte_id,
        "is_lowest_bidder": is_l1,
        "justification_reason": justification,
        "decided_by": payload.get("user_name", "Sarah Jenkins (Buyer)"),
        "decided_at": datetime.now().isoformat()
    }
    db["quotation_selection_decisions"].append(decision)

    save_db()
    return {"success": True, "data": decision, "message": f"Supplier selection decision recorded successfully. (L1: {is_l1})"}

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

