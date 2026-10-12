from fastapi import APIRouter, Request, Header, HTTPException
from db.database_store import db, save_db, add_notification
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import os

router = APIRouter(prefix="/api/billing", tags=["Billing"])


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class CustomerSchema(BaseModel):
    id: Optional[str] = None
    name: str
    phone: Optional[str] = ""
    email: Optional[str] = ""
    address: Optional[str] = ""
    state: Optional[str] = ""
    gstin: Optional[str] = ""
    is_walk_in: Optional[bool] = True


class BillItemSchema(BaseModel):
    product_id: str
    quantity: float
    unit_price: Optional[float] = None   # frontend hint; backend re-validates
    mrp: Optional[float] = None
    discount: Optional[float] = 0.0      # percentage 0-100
    warehouse_id: Optional[str] = "wh-01"


class CreateInvoiceSchema(BaseModel):
    customer: CustomerSchema
    items: List[BillItemSchema]
    payment_method: str = "Cash"
    amount_paid: Optional[float] = 0.0
    transaction_id: Optional[str] = ""
    gateway_reference: Optional[str] = ""
    sale_type: Optional[str] = "intra"   # "intra" or "inter"
    notes: Optional[str] = ""
    warehouse_id: Optional[str] = "wh-01"


class ReturnItemSchema(BaseModel):
    invoice_item_id: str
    product_id: str
    quantity: float
    reason: Optional[str] = ""


class CreateReturnSchema(BaseModel):
    invoice_id: str
    items: List[ReturnItemSchema]
    reason: Optional[str] = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_auth_context(request: Request, x_user_email=None, x_company_name=None, x_user_role=None):
    email   = x_user_email   or request.headers.get("x-user-email")   or ""
    company = x_company_name or request.headers.get("x-company-name") or "Organization"
    role    = x_user_role    or request.headers.get("x-user-role")    or ""
    return email, company, role


# ── Billing Settings Configuration ──────────────────────────────────────────

DEFAULT_BILLING_SETTINGS = {
    "store_name": "AMMUS SUPERMARKET",
    "store_subtitle": "Fresh Grocery & Supermarket",
    "store_address": "JUNCTION ROAD, NEAR BUS STAND, TRIVANDRUM",
    "store_phone": "9895820417, 0471-224488",
    "store_email": "contact@ammussupermarket.com",
    "gstin": "32DPHPB3199N1ZL",
    "fssai": "11324001000001",
    "bill_prefix": "SH/25-27/",
    "bill_sequence_start": 1,
    "bill_sequence_padding": 7,
    "default_gst_rate": 5.0,
    "cgst_rate": 2.5,
    "sgst_rate": 2.5,
    "igst_rate": 5.0,
    "enable_gst": True,
    "enable_round_off": True,
    "enable_discounts": True,
    "max_discount_pct": 25.0,
    "default_discount_pct": 0.0,
    "invoice_title": "TAX INVOICE",
    "footer_greeting": "**** Thank You Visit Again ****",
    "savings_text": "You Have Saved Rs.",
    "footer_note": "Exchange within 7 days with original bill. Thank you!",
    "paper_width": "80mm",
    "show_cashier": True,
    "show_barcode": True,
    "bill_theme": "supermarket",  # "supermarket" | "software" | "furniture" | "custom"
    "custom_theme_config": None,
}

def get_billing_settings_data() -> Dict[str, Any]:
    if "settings" not in db or not isinstance(db.get("settings"), dict):
        db["settings"] = {}
    stored = db["settings"].get("billing_settings")
    if not stored or not isinstance(stored, dict):
        db["settings"]["billing_settings"] = dict(DEFAULT_BILLING_SETTINGS)
        save_db("settings")
        return db["settings"]["billing_settings"]
    for k, v in DEFAULT_BILLING_SETTINGS.items():
        if k not in stored:
            stored[k] = v
    return stored


def get_next_invoice_number() -> str:
    """
    Generate sequential bill number using configured prefix and padding from billing settings.
    """
    bsettings = get_billing_settings_data()
    prefix = bsettings.get("bill_prefix", "SH/25-27/")
    padding = int(bsettings.get("bill_sequence_padding", 7))
    start_seq = int(bsettings.get("bill_sequence_start", 1))

    invoices = db.get("invoices", [])
    max_seq = 0
    for inv in invoices:
        num = inv.get("invoice_number", "")
        if num.startswith(prefix):
            try:
                seq = int(num[len(prefix):])
                if seq > max_seq:
                    max_seq = seq
            except ValueError:
                pass
    next_seq = max(max_seq + 1, start_seq) if max_seq == 0 else (max_seq + 1)
    return f"{prefix}{str(next_seq).zfill(padding)}"


def get_return_number() -> str:
    year = datetime.now().year
    returns = db.get("returns", [])
    max_seq = 0
    prefix = f"RET-{year}-"
    for r in returns:
        num = r.get("return_number", "")
        if num.startswith(prefix):
            try:
                seq = int(num[len(prefix):])
                if seq > max_seq:
                    max_seq = seq
            except ValueError:
                pass
    return f"{prefix}{str(max_seq + 1).zfill(6)}"


def calculate_gst(taxable_amount: float, gst_rate: float, sale_type: str):
    """Return (cgst, sgst, igst) amounts."""
    total_gst = round(taxable_amount * gst_rate / 100, 2)
    if sale_type == "inter":
        return 0.0, 0.0, total_gst
    else:
        half = round(total_gst / 2, 2)
        return half, half, 0.0


def _get_item_stock(item_id: str, warehouse_id: str = None) -> float:
    """Return available qty from inventory_balances or item master."""
    balances = db.get("inventory_balances", [])
    total = 0.0
    found = False
    for bal in balances:
        if bal.get("item_id") != item_id and bal.get("item_code") != item_id:
            continue
        if warehouse_id and bal.get("warehouse_id") != warehouse_id:
            continue
        total += float(bal.get("available_qty", bal.get("quantity", 0)))
        found = True
    if not found or total <= 0:
        item = next((i for i in db.get("items", []) if i.get("id") == item_id or i.get("item_code") == item_id or i.get("sku") == item_id), None)
        if item:
            total = float(item.get("available_qty", item.get("on_hand_qty", 0)))
    return total


def _reduce_stock(item_id: str, quantity: float, warehouse_id: str, biller_email: str, invoice_number: str):
    """Reduce inventory_balances.available_qty and item available_qty, and log in inventory_ledger."""
    remaining = quantity
    balances = db.get("inventory_balances", [])
    for bal in balances:
        if bal.get("item_id") != item_id and bal.get("item_code") != item_id:
            continue
        if warehouse_id and bal.get("warehouse_id") != warehouse_id:
            continue
        avail = float(bal.get("available_qty", bal.get("quantity", 0)))
        deduct = min(avail, remaining)
        bal["available_qty"] = max(0, avail - deduct)
        bal["quantity"] = max(0, float(bal.get("quantity", 0)) - deduct)
        remaining -= deduct
        if remaining <= 0:
            break

    # Also reduce item master available_qty
    for itm in db.get("items", []):
        if itm.get("id") == item_id or itm.get("item_code") == item_id or itm.get("sku") == item_id:
            cur = float(itm.get("available_qty", 0))
            itm["available_qty"] = max(0, cur - quantity)
            itm["on_hand_qty"] = max(0, float(itm.get("on_hand_qty", cur)) - quantity)
            break

    # Log to inventory ledger
    if "inventory_ledger" not in db:
        db["inventory_ledger"] = []
    item = next((i for i in db.get("items", []) if i.get("id") == item_id or i.get("item_code") == item_id), {})
    db["inventory_ledger"].insert(0, {
        "id": f"ledg-bill-{len(db['inventory_ledger']) + 1}",
        "posting_date": datetime.now().strftime("%Y-%m-%d"),
        "item_id": item_id,
        "item_name": item.get("name", item.get("item_name", "")),
        "warehouse_id": warehouse_id,
        "voucher_type": "SALE",
        "voucher_no": invoice_number,
        "qty_in": 0,
        "qty_out": quantity,
        "balance_qty": _get_item_stock(item_id, warehouse_id),
        "valuation_rate": float(item.get("unit_price", item.get("valuation_rate", 0))),
        "created_by": biller_email,
        "company_name": "Organization",
        "created_at": datetime.now().isoformat()
    })


def _log_audit(action: str, user_email: str, entity_id: str, details: str):
    if "audit_logs" not in db:
        db["audit_logs"] = []
    db["audit_logs"].insert(0, {
        "id": f"aud-bill-{len(db['audit_logs']) + 1}",
        "timestamp": datetime.now().isoformat(),
        "user_id": user_email,
        "user_name": user_email,
        "action": action,
        "category": "Billing",
        "module": "Billing Module",
        "record_id": entity_id,
        "ip_address": "127.0.0.1",
        "details": details,
        "old_value": None,
        "new_value": None,
        "reason": "Billing Operation"
    })


# ── Billing Master Endpoints ──────────────────────────────────────────────────

@router.get("/invoice-number")
def get_next_invoice_no():
    """Fetch the next available invoice number without consuming it."""
    return {"success": True, "invoice_number": get_next_invoice_number()}


@router.get("/settings")
def get_billing_settings():
    """Fetch current supermarket billing configuration."""
    return {"success": True, "data": get_billing_settings_data()}


@router.put("/settings")
@router.post("/settings")
def update_billing_settings(
    payload: Dict[str, Any],
    request: Request,
    x_user_email: str = Header(None)
):
    """
    Update supermarket billing configuration and persist to PostgreSQL settings table.
    Changes apply to store name, tax rates, bill series, receipt headers & footers.
    """
    email = x_user_email or "admin@company.com"
    curr = get_billing_settings_data()
    for k, v in payload.items():
        curr[k] = v

    if "settings" not in db:
        db["settings"] = {}
    db["settings"]["billing_settings"] = curr

    # Save to PostgreSQL table 'settings'
    save_db("settings")

    _log_audit("BILLING_SETTINGS_UPDATED", email, "billing_settings", f"Updated store billing settings for {curr.get('store_name')}")

    return {
        "success": True,
        "message": "Billing settings saved successfully.",
        "data": curr
    }


@router.get("/categories")
def get_billing_categories():
    """Return all supermarket product categories with item counts."""
    categories = db.get("item_categories", [])
    items = db.get("items", [])
    cat_counts = {}
    for it in items:
        cid = it.get("category_id", "")
        cat_counts[cid] = cat_counts.get(cid, 0) + 1

    data = []
    for c in categories:
        data.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "code": c.get("code", ""),
            "count": cat_counts.get(c.get("id"), 0)
        })
    return {"success": True, "data": data}


@router.get("/products/search")
def search_billing_products(
    request: Request,
    q: str = "",
    warehouse_id: str = "wh-01",
    category_id: str = "",
    x_user_email: str = Header(None),
    x_company_name: str = Header(None),
    x_user_role: str = Header(None)
):
    """
    Search products by name, item_code, barcode, SKU, brand, category.
    Returns product info + live stock from inventory_balances.
    """
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    query = (q or "").lower().strip()

    items = db.get("items", [])
    tax_rates = db.get("tax_rates", [])
    tax_map = {t["id"]: t for t in tax_rates}
    cat_map = {c["id"]: c.get("name", "") for c in db.get("item_categories", [])}
    brd_map = {b["id"]: b.get("name", "") for b in db.get("brands", [])}

    results = []
    for item in items:
        # Category filter
        item_cat = item.get("category_id", "")
        if category_id and category_id.lower() != "all" and item_cat != category_id:
            continue

        cat_name = item.get("category_name") or cat_map.get(item_cat, "Grocery")
        brand_name = item.get("brand_name") or brd_map.get(item.get("brand_id", ""), "General")

        # Search filter
        if query:
            searchable = " ".join([
                item.get("item_code", ""),
                item.get("name", item.get("item_name", "")),
                item.get("barcode", ""),
                item.get("sku", ""),
                brand_name,
                cat_name
            ]).lower()
            if query not in searchable:
                continue

        # Resolve selling price & MRP
        selling_price = float(item.get("unit_price", item.get("selling_price", item.get("valuation_rate", 0))))
        raw_mrp = item.get("mrp") or item.get("max_retail_price")
        mrp = float(raw_mrp) if raw_mrp else round(selling_price * 1.08, 2)
        if mrp < selling_price:
            mrp = selling_price

        cost_price = float(item.get("cost_price", item.get("valuation_rate", round(selling_price * 0.8, 2))))

        # Resolve GST
        tax_rate_id = item.get("tax_rate_id", "")
        if item.get("enable_gst") is False:
            gst_rate = 0.0
        else:
            gst_rate = float(item.get("gst_rate") if item.get("gst_rate") is not None else (item.get("tax_percentage") or 0.0))
            if gst_rate == 0.0 and tax_rate_id and tax_rate_id in tax_map:
                gst_rate = float(tax_map[tax_rate_id].get("percentage", 0.0))
        hsn_sac = item.get("hsn_sac_code") or item.get("hsn_code") or item.get("hsn") or ""
        if not hsn_sac:
            clean_seed = abs(hash(item.get("id", "item1000"))) % 90000000 + 10000000
            hsn_sac = str(clean_seed)

        # Resolve UOM symbol
        uom_id = item.get("uom_id", "")
        uom = next((u for u in db.get("units_of_measure", []) if u["id"] == uom_id), {})
        uom_symbol = uom.get("unit_symbol", item.get("unit", "Pcs"))

        # Stock availability
        available_stock = _get_item_stock(item.get("id"), warehouse_id)

        results.append({
            "id": item.get("id"),
            "item_code": item.get("item_code", ""),
            "name": item.get("name", item.get("item_name", "")),
            "sku": item.get("sku", item.get("item_code", "")),
            "barcode": item.get("barcode", ""),
            "hsn_sac": hsn_sac,
            "unit_price": selling_price,
            "mrp": mrp,
            "cost_price": cost_price,
            "gst_rate": gst_rate,
            "tax_rate_id": tax_rate_id,
            "uom_symbol": uom_symbol,
            "available_stock": available_stock,
            "min_stock": item.get("min_stock", 5),
            "category_id": item_cat,
            "category_name": cat_name,
            "brand_id": item.get("brand_id", ""),
            "brand_name": brand_name,
            "discount": float(item.get("discount", 0.0)),
            "offer": item.get("offer", "None"),
            "status": item.get("status", "Active"),
            "description": item.get("description", ""),
        })

    results.sort(key=lambda x: x["name"])
    return {"success": True, "data": results[:300]}


@router.get("/customers")
def get_all_billing_customers(
    search: str = "",
    page: int = 1,
    limit: int = 50
):
    customers = list(db.get("billing_customers", []))
    if search:
        s = search.lower().strip()
        customers = [
            c for c in customers
            if s in (c.get("name", "") + c.get("phone", "") + c.get("email", "") + c.get("address", "")).lower()
        ]
    customers.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    total = len(customers)
    offset = (page - 1) * limit
    return {"success": True, "data": customers[offset: offset + limit], "total": total}


@router.get("/customers/search")
def search_billing_customers(
    request: Request,
    q: str = "",
    x_user_email: str = Header(None),
    x_company_name: str = Header(None)
):
    """Search customers stored in billing_customers table."""
    query = (q or "").lower().strip()
    customers = db.get("billing_customers", [])
    if query:
        customers = [
            c for c in customers
            if query in (c.get("name", "") + c.get("phone", "") + c.get("email", "")).lower()
        ]
    return {"success": True, "data": customers[:30]}


@router.post("/customers")
def create_customer(
    payload: Dict[str, Any],
    request: Request,
    x_user_email: str = Header(None),
    x_company_name: str = Header(None)
):
    email, company, _ = get_auth_context(request, x_user_email, x_company_name)
    if "billing_customers" not in db:
        db["billing_customers"] = []

    cid = f"cust-{len(db['billing_customers']) + 1001}"
    customer = {
        "id": cid,
        "name": payload.get("name", "Walk-in Customer"),
        "phone": payload.get("phone", ""),
        "email": payload.get("email", ""),
        "address": payload.get("address", ""),
        "state": payload.get("state", ""),
        "gstin": payload.get("gstin", ""),
        "company_name": company,
        "created_by": email,
        "created_at": datetime.now().isoformat()
    }
    db["billing_customers"].append(customer)
    save_db("billing_customers")
    return {"success": True, "data": customer}


@router.post("/invoices")
def create_invoice(
    req: CreateInvoiceSchema,
    request: Request,
    x_user_email: str = Header(None),
    x_company_name: str = Header(None),
    x_user_role: str = Header(None)
):
    """
    Create a complete invoice with:
    - Backend price/GST validation
    - Stock validation & reduction
    - Invoice + Invoice Items + Payment records
    - Audit log
    - Transactional safety (all-or-nothing in db dict before save)
    """
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)

    # ── 1. Generate Invoice Number ──────────────────────────────────────────
    invoice_number = get_next_invoice_number()

    # ── 2. Validate + Build Line Items ──────────────────────────────────────
    items_payload = []
    subtotal = 0.0
    total_discount_amount = 0.0
    total_cgst = 0.0
    total_sgst = 0.0
    total_igst = 0.0

    tax_rates = {t["id"]: t for t in db.get("tax_rates", [])}
    all_items = {i["id"]: i for i in db.get("items", [])}

    for line in req.items:
        item = all_items.get(line.product_id)
        if not item:
            raise HTTPException(status_code=400, detail=f"Product '{line.product_id}' not found.")

        qty = float(line.quantity)
        if qty <= 0:
            raise HTTPException(status_code=400, detail=f"Quantity must be positive for product '{item.get('name', line.product_id)}'.")

        # Stock check
        avail = _get_item_stock(line.product_id, line.warehouse_id or req.warehouse_id)
        if avail < qty:
            name = item.get("name", item.get("item_name", line.product_id))
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{name}'. Available: {avail:.0f} units. Requested: {qty:.0f} units."
            )

        # Price and MRP
        unit_price = float(item.get("unit_price", item.get("selling_price", item.get("valuation_rate", 0))))
        item_mrp = float(line.mrp or item.get("mrp") or round(unit_price * 1.05, 2))
        if item_mrp < unit_price:
            item_mrp = unit_price

        # Discount validation (0-100%)
        discount_pct = max(0.0, min(100.0, float(line.discount or 0)))
        discount_amount = round(unit_price * qty * discount_pct / 100, 2)

        line_subtotal = round(unit_price * qty, 2)
        taxable_value = round(line_subtotal - discount_amount, 2)

        # GST
        tax_rate_id = item.get("tax_rate_id", "")
        gst_rate = float(tax_rates[tax_rate_id].get("percentage", 0)) if tax_rate_id in tax_rates else 0.0
        cgst, sgst, igst = calculate_gst(taxable_value, gst_rate, req.sale_type)
        tax_amount = round(cgst + sgst + igst, 2)
        line_total = round(taxable_value + tax_amount, 2)

        # Snapshots for historical accuracy
        uom_id = item.get("uom_id", "")
        uom = next((u for u in db.get("units_of_measure", []) if u["id"] == uom_id), {})

        hsn_sac_val = item.get("hsn_sac_code") or item.get("hsn_code") or item.get("hsn") or ""
        if not hsn_sac_val:
            hsn_sac_val = str(abs(hash(item.get("id", "item1000"))) % 90000000 + 10000000)

        items_payload.append({
            "id": f"ii-{invoice_number}-{line.product_id}",
            "invoice_id": "",       # filled after invoice created
            "product_id": line.product_id,
            "product_name_snapshot": item.get("name", item.get("item_name", "")),
            "sku_snapshot": item.get("item_code", item.get("sku", "")),
            "hsn_sac_snapshot": hsn_sac_val,
            "barcode": item.get("barcode", ""),
            "quantity": qty,
            "unit_price": unit_price,
            "mrp": item_mrp,
            "discount_pct": discount_pct,
            "discount_amount": discount_amount,
            "taxable_value": taxable_value,
            "gst_rate": gst_rate,
            "cgst": cgst,
            "sgst": sgst,
            "igst": igst,
            "tax_amount": tax_amount,
            "line_total": line_total,
            "uom_symbol": uom.get("unit_symbol", "Pcs"),
            "warehouse_id": line.warehouse_id or req.warehouse_id,
            "created_at": datetime.now().isoformat()
        })

        subtotal += line_subtotal
        total_discount_amount += discount_amount
        total_cgst += cgst
        total_sgst += sgst
        total_igst += igst

    subtotal = round(subtotal, 2)
    total_discount_amount = round(total_discount_amount, 2)
    taxable_amount = round(subtotal - total_discount_amount, 2)
    total_cgst = round(total_cgst, 2)
    total_sgst = round(total_sgst, 2)
    total_igst = round(total_igst, 2)
    total_gst = round(total_cgst + total_sgst + total_igst, 2)
    grand_total_raw = taxable_amount + total_gst
    round_off = round(round(grand_total_raw) - grand_total_raw, 2)
    grand_total = round(taxable_amount + total_gst + round_off, 2)

    # Supermarket Receipt Gross Bill Total & Savings
    bill_total = round(sum(li.get("mrp", li["unit_price"]) * li["quantity"] for li in items_payload), 2)
    if bill_total < grand_total:
        bill_total = grand_total
    savings = round(bill_total - grand_total, 2)

    # ── 3. Payment Status ────────────────────────────────────────────────────
    amount_paid = float(req.amount_paid or 0)
    if amount_paid >= grand_total:
        payment_status = "Paid"
        invoice_status = "Completed"
    elif amount_paid > 0:
        payment_status = "Partially Paid"
        invoice_status = "Partially Paid"
    else:
        payment_status = "Pending"
        invoice_status = "Pending Payment"

    change_amount = max(0, round(amount_paid - grand_total, 2))

    # ── 4. Customer record (save/reuse) ──────────────────────────────────────
    if "billing_customers" not in db:
        db["billing_customers"] = []
    customer = req.customer
    cust_id = customer.id
    if not cust_id or customer.is_walk_in:
        cust_id = f"cust-walkin-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cust_record = {
            "id": cust_id,
            "name": customer.name or "Walk-in Customer",
            "phone": customer.phone or "",
            "email": customer.email or "",
            "address": customer.address or "",
            "state": customer.state or "",
            "gstin": customer.gstin or "",
            "is_walk_in": True,
            "company_name": company,
            "created_by": email,
            "created_at": datetime.now().isoformat()
        }
        db["billing_customers"].append(cust_record)

    # ── 5. Build Invoice ─────────────────────────────────────────────────────
    invoice_id = f"inv-{len(db.get('invoices', [])) + 1001}"

    invoice = {
        "id": invoice_id,
        "invoice_number": invoice_number,
        "customer_id": cust_id,
        "customer_name": customer.name or "Walk-in Customer",
        "customer_phone": customer.phone or "",
        "customer_email": customer.email or "",
        "customer_address": customer.address or "",
        "customer_state": customer.state or "",
        "customer_gstin": customer.gstin or "",
        "biller_id": email,
        "biller_name": email,
        "company_name": company,
        "sale_type": req.sale_type,
        "subtotal": subtotal,
        "discount": total_discount_amount,
        "taxable_amount": taxable_amount,
        "cgst": total_cgst,
        "sgst": total_sgst,
        "igst": total_igst,
        "total_gst": total_gst,
        "round_off": round_off,
        "grand_total": grand_total,
        "bill_total": bill_total,
        "savings": savings,
        "payment_status": payment_status,
        "invoice_status": invoice_status,
        "payment_method": req.payment_method,
        "amount_paid": amount_paid,
        "balance_due": max(0, round(grand_total - amount_paid, 2)),
        "change_amount": change_amount,
        "transaction_id": req.transaction_id or "",
        "gateway_reference": req.gateway_reference or "",
        "notes": req.notes or "",
        "warehouse_id": req.warehouse_id,
        "items_count": len(items_payload),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    # Fill invoice_id into items
    for line_item in items_payload:
        line_item["invoice_id"] = invoice_id

    # ── 6. Payment record ────────────────────────────────────────────────────
    payment_record = {
        "id": f"pay-{invoice_id}",
        "invoice_id": invoice_id,
        "payment_method": req.payment_method,
        "amount": amount_paid,
        "status": payment_status,
        "transaction_id": req.transaction_id or "",
        "gateway_reference": req.gateway_reference or "",
        "paid_at": datetime.now().isoformat() if amount_paid > 0 else None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    # ── 7. Commit all changes atomically ─────────────────────────────────────
    # Init tables
    for tbl in ["invoices", "invoice_items", "payments", "returns", "return_items"]:
        if tbl not in db:
            db[tbl] = []

    db["invoices"].insert(0, invoice)
    for li in items_payload:
        db["invoice_items"].append(li)
    db["payments"].append(payment_record)

    # Reduce stock for each line
    for li in items_payload:
        _reduce_stock(li["product_id"], li["quantity"], li["warehouse_id"], email, invoice_number)

    # Audit log
    _log_audit("INVOICE_CREATED", email, invoice_id, f"Invoice {invoice_number} created. Grand Total: ₹{grand_total}")

    # Notification
    add_notification(
        title=f"Invoice {invoice_number} Created",
        message=f"Bill of ₹{grand_total:.2f} by {email} for customer {customer.name}",
        notif_type="success",
        target_role="ALL"
    )

    # Save to PostgreSQL
    save_db("invoices")
    save_db("invoice_items")
    save_db("payments")
    save_db("inventory_balances")
    save_db("items")
    save_db("inventory_ledger")
    save_db("billing_customers")
    save_db("audit_logs")

    return {
        "success": True,
        "message": f"Invoice {invoice_number} created successfully.",
        "data": {
            "invoice": invoice,
            "items": items_payload,
            "payment": payment_record
        }
    }


@router.get("/invoices")
def get_invoices(
    request: Request,
    page: int = 1,
    limit: int = 20,
    status: str = "",
    payment_method: str = "",
    search: str = "",
    date_from: str = "",
    date_to: str = "",
    x_user_email: str = Header(None),
    x_company_name: str = Header(None),
    x_user_role: str = Header(None)
):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    invoices = list(db.get("invoices", []))

    # Filters
    if status:
        invoices = [i for i in invoices if i.get("payment_status", "").lower() == status.lower()]
    if payment_method:
        invoices = [i for i in invoices if i.get("payment_method", "").lower() == payment_method.lower()]
    if search:
        s = search.lower()
        invoices = [
            i for i in invoices
            if s in i.get("invoice_number", "").lower()
            or s in i.get("customer_name", "").lower()
            or s in i.get("customer_phone", "").lower()
            or s in i.get("customer_email", "").lower()
            or s in i.get("customer_address", "").lower()
        ]
    if date_from:
        invoices = [i for i in invoices if i.get("created_at", "") >= date_from]
    if date_to:
        invoices = [i for i in invoices if i.get("created_at", "") <= date_to + "T23:59:59"]

    invoices.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    total = len(invoices)
    offset = (page - 1) * limit
    paginated = invoices[offset: offset + limit]

    return {"success": True, "data": paginated, "total": total, "page": page, "limit": limit}


@router.get("/invoices/{invoice_id}")
def get_invoice_detail(
    invoice_id: str,
    request: Request,
    x_user_email: str = Header(None)
):
    invoice = next(
        (i for i in db.get("invoices", []) if i.get("id") == invoice_id or i.get("invoice_number") == invoice_id),
        None
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    items = [i for i in db.get("invoice_items", []) if i.get("invoice_id") == invoice.get("id")]
    payment = next((p for p in db.get("payments", []) if p.get("invoice_id") == invoice.get("id")), None)

    return {"success": True, "data": {"invoice": invoice, "items": items, "payment": payment}}


@router.patch("/invoices/{invoice_id}/payment")
def update_payment(
    invoice_id: str,
    payload: Dict[str, Any],
    request: Request,
    x_user_email: str = Header(None)
):
    """Update payment status after gateway callback or manual update."""
    invoice = next((i for i in db.get("invoices", []) if i.get("id") == invoice_id), None)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    # Idempotency guard
    if invoice.get("payment_status") == "Paid":
        return {"success": True, "message": "Invoice already marked as paid.", "data": invoice}

    new_status = payload.get("payment_status", "Paid")
    amount_paid = float(payload.get("amount_paid", invoice.get("grand_total", 0)))
    transaction_id = payload.get("transaction_id", "")
    gateway_reference = payload.get("gateway_reference", "")

    invoice["payment_status"] = new_status
    invoice["amount_paid"] = amount_paid
    invoice["balance_due"] = max(0, round(float(invoice["grand_total"]) - amount_paid, 2))
    invoice["transaction_id"] = transaction_id or invoice.get("transaction_id", "")
    invoice["gateway_reference"] = gateway_reference or invoice.get("gateway_reference", "")
    invoice["updated_at"] = datetime.now().isoformat()
    if new_status == "Paid":
        invoice["invoice_status"] = "Completed"

    # Update payment record
    for pay in db.get("payments", []):
        if pay.get("invoice_id") == invoice_id:
            pay["status"] = new_status
            pay["amount"] = amount_paid
            pay["transaction_id"] = transaction_id or pay.get("transaction_id", "")
            pay["paid_at"] = datetime.now().isoformat()
            pay["updated_at"] = datetime.now().isoformat()

    email = x_user_email or ""
    _log_audit("PAYMENT_RECEIVED", email, invoice_id, f"Payment updated to {new_status} for invoice {invoice.get('invoice_number')}.")
    save_db("invoices")
    save_db("payments")
    return {"success": True, "data": invoice}


@router.patch("/invoices/{invoice_id}/cancel")
def cancel_invoice(
    invoice_id: str,
    payload: Dict[str, Any],
    request: Request,
    x_user_email: str = Header(None)
):
    invoice = next((i for i in db.get("invoices", []) if i.get("id") == invoice_id), None)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    if invoice.get("payment_status") == "Paid":
        raise HTTPException(status_code=400, detail="Cannot cancel a paid invoice. Use return/refund instead.")

    invoice["payment_status"] = "Cancelled"
    invoice["invoice_status"] = "Cancelled"
    invoice["updated_at"] = datetime.now().isoformat()

    email = x_user_email or ""
    _log_audit("INVOICE_CANCELLED", email, invoice_id, f"Invoice {invoice.get('invoice_number')} cancelled.")
    save_db("invoices")
    return {"success": True, "message": "Invoice cancelled.", "data": invoice}


@router.post("/returns")
def create_return(
    req: CreateReturnSchema,
    request: Request,
    x_user_email: str = Header(None),
    x_company_name: str = Header(None)
):
    email, company, _ = get_auth_context(request, x_user_email, x_company_name)

    invoice = next((i for i in db.get("invoices", []) if i.get("id") == req.invoice_id), None)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    return_number = get_return_number()
    return_id = f"ret-{len(db.get('returns', [])) + 1001}"

    for tbl in ["returns", "return_items"]:
        if tbl not in db:
            db[tbl] = []

    # Process return items
    return_items_payload = []
    refund_total = 0.0
    invoice_items_map = {i.get("id"): i for i in db.get("invoice_items", []) if i.get("invoice_id") == req.invoice_id}

    for ri in req.items:
        inv_item = invoice_items_map.get(ri.invoice_item_id)
        if not inv_item:
            raise HTTPException(status_code=400, detail=f"Invoice item '{ri.invoice_item_id}' not found.")

        max_returnable = float(inv_item.get("quantity", 0))
        return_qty = float(ri.quantity)
        if return_qty > max_returnable:
            raise HTTPException(status_code=400, detail=f"Return quantity {return_qty} exceeds sold quantity {max_returnable}.")

        line_total = float(inv_item.get("line_total", 0))
        sold_qty = float(inv_item.get("quantity", 1))
        unit_refund = round(line_total / sold_qty * return_qty, 2)
        refund_total += unit_refund

        return_items_payload.append({
            "id": f"reti-{return_id}-{ri.invoice_item_id}",
            "return_id": return_id,
            "invoice_item_id": ri.invoice_item_id,
            "product_id": ri.product_id,
            "quantity": return_qty,
            "refund_amount": unit_refund,
            "reason": ri.reason or "",
            "created_at": datetime.now().isoformat()
        })

        # Restock inventory
        wh_id = inv_item.get("warehouse_id", invoice.get("warehouse_id", "wh-01"))
        balances = db.get("inventory_balances", [])
        restocked = False
        for bal in balances:
            if bal.get("item_id") == ri.product_id and bal.get("warehouse_id") == wh_id:
                bal["available_qty"] = float(bal.get("available_qty", 0)) + return_qty
                bal["quantity"] = float(bal.get("quantity", 0)) + return_qty
                restocked = True
                break
        if not restocked:
            # Add a new balance record
            item_obj = next((i for i in db.get("items", []) if i["id"] == ri.product_id), {})
            db["inventory_balances"].append({
                "id": f"bal-ret-{return_id}-{ri.product_id}",
                "item_id": ri.product_id,
                "item_name": item_obj.get("name", ""),
                "warehouse_id": wh_id,
                "quantity": return_qty,
                "available_qty": return_qty,
                "reserved_qty": 0,
                "created_at": datetime.now().isoformat()
            })

    refund_total = round(refund_total, 2)

    return_record = {
        "id": return_id,
        "return_number": return_number,
        "invoice_id": req.invoice_id,
        "invoice_number": invoice.get("invoice_number", ""),
        "customer_id": invoice.get("customer_id", ""),
        "customer_name": invoice.get("customer_name", ""),
        "processed_by": email,
        "reason": req.reason or "",
        "refund_amount": refund_total,
        "refund_status": "Refunded",
        "company_name": company,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    db["returns"].append(return_record)
    for ri_payload in return_items_payload:
        db["return_items"].append(ri_payload)

    # Update invoice refund status
    invoice["payment_status"] = "Refunded"
    invoice["updated_at"] = datetime.now().isoformat()

    _log_audit("RETURN_CREATED", email, return_id, f"Return {return_number} for invoice {invoice.get('invoice_number')}. Refund: ₹{refund_total}.")

    save_db("returns")
    save_db("return_items")
    save_db("invoices")
    save_db("inventory_balances")
    save_db("audit_logs")

    return {"success": True, "data": {"return": return_record, "items": return_items_payload}}


@router.get("/returns")
def get_returns(
    request: Request,
    x_user_email: str = Header(None),
    x_company_name: str = Header(None)
):
    returns = db.get("returns", [])
    returns.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"success": True, "data": returns}


@router.get("/returns/{return_id}")
def get_return_detail(return_id: str):
    ret = next((r for r in db.get("returns", []) if r.get("id") == return_id), None)
    if not ret:
        raise HTTPException(status_code=404, detail="Return not found.")
    items = [ri for ri in db.get("return_items", []) if ri.get("return_id") == return_id]
    return {"success": True, "data": {"return": ret, "items": items}}


@router.get("/summary")
def billing_summary(
    request: Request,
    x_user_email: str = Header(None),
    x_company_name: str = Header(None)
):
    """Quick billing dashboard summary."""
    invoices = db.get("invoices", [])
    today = datetime.now().date().isoformat()

    today_invoices = [i for i in invoices if i.get("created_at", "")[:10] == today]
    total_today = sum(float(i.get("grand_total", 0)) for i in today_invoices)
    paid_today = sum(float(i.get("amount_paid", 0)) for i in today_invoices if i.get("payment_status") == "Paid")
    pending_count = len([i for i in invoices if i.get("payment_status") == "Pending"])
    total_invoices = len(invoices)

    return {
        "success": True,
        "data": {
            "total_invoices": total_invoices,
            "today_invoices": len(today_invoices),
            "today_total": total_today,
            "today_paid": paid_today,
            "pending_count": pending_count,
            "total_gst_today": sum(float(i.get("total_gst", 0)) for i in today_invoices)
        }
    }
