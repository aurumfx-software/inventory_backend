from fastapi import APIRouter, Request, Header
from db.database_store import db, save_db, filter_by_company, filter_by_user_or_company
from schemas.schemas import ItemCreate, SupplierCreate
from datetime import datetime
from urllib.parse import unquote
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["Masters"])

def get_auth_context(request: Request, x_user_email: str = None, x_company_name: str = None, x_user_role: str = None):
    email = x_user_email or request.headers.get("x-user-email") or request.query_params.get("user_email") or ""
    company = x_company_name or request.headers.get("x-company-name") or request.query_params.get("company_name") or "Organization"
    role = x_user_role or request.headers.get("x-user-role") or request.query_params.get("role_id") or ""
    return email, company, role

# =========================================================================
# ITEMS MASTER & ALIASES
# =========================================================================
@router.get("/items")
def get_items(request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    data = filter_by_user_or_company(db.get("items", []), email, company, role)
    return {"success": True, "data": data}

@router.get("/items/search")
def search_items(request: Request, q: str = "", x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    scoped_items = filter_by_user_or_company(db.get("items", []), email, company, role)
    query = q.lower().strip()
    filtered = [
        i for i in scoped_items
        if query in i.get("item_code", "").lower() or query in i.get("item_name", "").lower()
    ]
    return {"success": True, "data": filtered}

@router.post("/items/import")
def import_items(payload: Dict[str, Any], request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, None)
    rows = payload.get("rows", [])
    count = 0
    for r in rows:
        if r.get("item_code") and r.get("item_name"):
            new_id = f"itm-{len(db['items']) + 1}"
            db["items"].append({
                "id": new_id,
                "item_code": r.get("item_code"),
                "item_name": r.get("item_name"),
                "company_name": company,
                "created_by": email,
                "is_sample": False,
                "valuation_rate": float(r.get("valuation_rate", 1000)),
                "category_id": "cat-01",
                "uom_id": "uom-01",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            })
            count += 1
    save_db("items")
    return {"success": True, "message": f"Successfully imported {count} items."}

@router.get("/items/export")
def export_items(request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    data = filter_by_user_or_company(db.get("items", []), email, company, role)
    return {"success": True, "data": data}

@router.get("/items/{item_id}")
def get_single_item(item_id: str):
    target = unquote(item_id).strip().lower()
    item = next((i for i in db["items"] if str(i.get("id", "")).lower() == target or str(i.get("item_code", "")).lower() == target), None)
    if item:
        return {"success": True, "data": item}
    return {"success": False, "message": "Item not found"}

@router.post("/items")
def create_item(item: ItemCreate, request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, None)
    new_id = f"itm-{str(len(db['items']) + 1).zfill(2)}"
    item_code = item.item_code or f"ITM-{datetime.now().strftime('%Y%m%d')}-{len(db['items']) + 1}"
    
    new_item = {
        "id": new_id,
        "item_code": item_code,
        "item_name": item.item_name,
        "company_name": company,
        "created_by": email,
        "is_sample": False,
        "description": item.description,
        "category_id": item.category_id or "cat-01",
        "brand_id": item.brand_id or "brd-01",
        "uom_id": item.uom_id or "uom-01",
        "purchase_uom_id": item.purchase_uom_id or "uom-01",
        "tax_rate_id": item.tax_rate_id or "tax-18",
        "hsn_sac_code": item.hsn_sac_code or "84713010",
        "min_stock_level": item.min_stock_level or 5,
        "max_stock_level": item.max_stock_level or 50,
        "reorder_level": item.reorder_level or 10,
        "reorder_qty": item.reorder_qty or 15,
        "valuation_rate": item.valuation_rate or 1000,
        "default_location_id": item.default_location_id or "loc-01",
        "is_batch_tracked": item.is_batch_tracked or False,
        "is_serial_tracked": item.is_serial_tracked or False,
        "is_expiry_tracked": item.is_expiry_tracked or False,
        "barcode": item.barcode or f"890123456789{len(db['items']) + 1}",
        "image_url": item.image_url or "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=300&auto=format&fit=crop&q=60",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    
    db["items"].append(new_item)

    balance_record = {
        "id": f"bal-{len(db['inventory_balances']) + 1}",
        "item_id": new_id,
        "warehouse_id": "wh-01",
        "location_id": "loc-01",
        "on_hand_qty": 20,
        "reserved_qty": 0,
        "available_qty": 20,
        "valuation_rate": item.valuation_rate or 1000,
        "created_by": email,
        "company_name": company
    }
    db["inventory_balances"].append(balance_record)
    save_db("items")
    save_db("inventory_balances")

    return {"success": True, "data": new_item}

@router.put("/items/{item_id}")
def update_item(item_id: str, payload: dict):
    target = unquote(item_id).strip().lower()
    for idx, item in enumerate(db["items"]):
        id_match = str(item.get("id", "")).strip().lower() == target
        code_match = str(item.get("item_code", "")).strip().lower() == target
        if id_match or code_match:
            db["items"][idx].update(payload)
            save_db()
            return {"success": True, "data": db["items"][idx]}
    return {"success": False, "message": "Item not found"}

@router.delete("/items/{item_id}")
def delete_item(item_id: str):
    target = unquote(item_id).strip().lower()
    initial_count = len(db["items"])
    db["items"] = [
        item for item in db["items"]
        if str(item.get("id", "")).strip().lower() != target
        and str(item.get("item_code", "")).strip().lower() != target
    ]
    if len(db["items"]) < initial_count:
        save_db()
        return {"success": True, "message": "Item deleted successfully"}
    return {"success": False, "message": "Item not found"}

# =========================================================================
# CATEGORIES, BRANDS, UOM & TAX ALIASES
# =========================================================================
@router.get("/categories")
@router.get("/item-categories")
@router.get("/masters/item-categories")
def get_categories():
    return {"success": True, "data": db["item_categories"]}

@router.post("/categories")
@router.post("/item-categories")
def create_category(payload: dict):
    new_id = payload.get("id") or f"cat-{str(len(db['item_categories']) + 1).zfill(2)}"
    new_cat = {
        "id": new_id,
        "category_code": payload.get("category_code") or f"CAT-{len(db['item_categories'])+1}",
        "category_name": payload.get("category_name") or payload.get("name", "New Category"),
        "description": payload.get("description", ""),
        "is_active": payload.get("is_active", True)
    }
    db["item_categories"].append(new_cat)
    save_db()
    return {"success": True, "data": new_cat}

@router.get("/brands")
def get_brands():
    return {"success": True, "data": db["brands"]}

@router.post("/brands")
def create_brand(payload: dict):
    new_id = payload.get("id") or f"brd-{str(len(db['brands']) + 1).zfill(2)}"
    new_brand = {
        "id": new_id,
        "brand_code": payload.get("brand_code") or f"BRD-{len(db['brands'])+1}",
        "brand_name": payload.get("brand_name") or payload.get("name", "New Brand"),
        "description": payload.get("description", ""),
        "is_active": payload.get("is_active", True)
    }
    db["brands"].append(new_brand)
    save_db()
    return {"success": True, "data": new_brand}

@router.get("/uom")
@router.get("/uoms")
@router.get("/units-of-measure")
def get_uom():
    return {"success": True, "data": db["units_of_measure"]}

@router.post("/uom")
@router.post("/uoms")
def create_uom(payload: dict):
    new_id = payload.get("id") or f"uom-{str(len(db['units_of_measure']) + 1).zfill(2)}"
    new_uom = {
        "id": new_id,
        "unit_name": payload.get("unit_name") or payload.get("name", "New Unit"),
        "unit_symbol": payload.get("unit_symbol") or payload.get("symbol", "Unit"),
        "is_active": payload.get("is_active", True)
    }
    db["units_of_measure"].append(new_uom)
    save_db()
    return {"success": True, "data": new_uom}

@router.get("/taxes")
@router.get("/tax-rates")
def get_tax_rates():
    return {"success": True, "data": db["tax_rates"]}

@router.post("/taxes")
@router.post("/tax-rates")
def create_tax_rate(payload: dict):
    new_id = payload.get("id") or f"tax-{str(len(db['tax_rates']) + 1).zfill(2)}"
    new_tax = {
        "id": new_id,
        "tax_name": payload.get("tax_name") or payload.get("name", "New Tax"),
        "tax_percentage": float(payload.get("tax_percentage") or payload.get("percentage", 18)),
        "tax_type": payload.get("tax_type", "GST"),
        "is_active": payload.get("is_active", True)
    }
    db["tax_rates"].append(new_tax)
    save_db()
    return {"success": True, "data": new_tax}

# =========================================================================
# SUPPLIERS MASTER
# =========================================================================
@router.get("/suppliers")
def get_suppliers(request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    data = filter_by_user_or_company(db.get("suppliers", []), email, company, role)
    return {"success": True, "data": data}

@router.get("/suppliers/{supplier_id}")
def get_supplier_by_id(supplier_id: str):
    target = unquote(supplier_id).strip().lower()
    sup = next((s for s in db["suppliers"] if str(s.get("id", "")).lower() == target or str(s.get("supplier_code", "")).lower() == target), None)
    if sup:
        return {"success": True, "data": sup}
    return {"success": False, "message": "Supplier not found"}

@router.get("/suppliers/{supplier_id}/items")
def get_supplier_items(supplier_id: str):
    return {"success": True, "data": db["items"][:2]}

@router.get("/suppliers/{supplier_id}/performance")
def get_supplier_performance(supplier_id: str):
    return {
        "success": True,
        "data": {
            "on_time_delivery_pct": 96.5,
            "quality_rejection_pct": 1.2,
            "avg_lead_time_days": 4,
            "rating": 4.8
        }
    }

@router.post("/suppliers/{supplier_id}/documents")
def add_supplier_document(supplier_id: str, payload: Dict[str, Any]):
    return {"success": True, "message": "Supplier document attached successfully."}

@router.post("/suppliers")
def create_supplier(sup: SupplierCreate, request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, None)
    new_id = f"sup-{str(len(db['suppliers']) + 1).zfill(2)}"
    sup_code = sup.supplier_code or f"SUP-{str(len(db['suppliers']) + 48).zfill(5)}"
    
    new_supplier = {
        "id": new_id,
        "supplier_code": sup_code,
        "supplier_name": sup.supplier_name,
        "company_name": company,
        "created_by": email,
        "is_sample": False,
        "contact_person": sup.contact_person,
        "phone": sup.phone,
        "email": sup.email,
        "address_registered": sup.address_registered,
        "gst_number": sup.gst_number,
        "pan_number": sup.pan_number,
        "payment_terms": sup.payment_terms,
        "delivery_lead_time_days": sup.delivery_lead_time_days,
        "rating": 4.5,
        "approval_status": "Approved",
        "is_active": True
    }
    db["suppliers"].append(new_supplier)
    save_db("suppliers")
    return {"success": True, "data": new_supplier}

@router.put("/suppliers/{supplier_id}")
def update_supplier(supplier_id: str, payload: dict):
    target = unquote(supplier_id).strip().lower()
    for idx, s in enumerate(db["suppliers"]):
        if str(s.get("id", "")).strip().lower() == target or str(s.get("supplier_code", "")).strip().lower() == target:
            db["suppliers"][idx].update(payload)
            save_db("suppliers")
            return {"success": True, "data": db["suppliers"][idx]}
    return {"success": False, "message": "Supplier not found"}

@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: str):
    target = unquote(supplier_id).strip().lower()
    initial_count = len(db["suppliers"])
    db["suppliers"] = [
        s for s in db["suppliers"]
        if str(s.get("id", "")).strip().lower() != target
        and str(s.get("supplier_code", "")).strip().lower() != target
    ]
    if len(db["suppliers"]) < initial_count:
        save_db("suppliers")
        return {"success": True, "message": "Supplier deleted successfully"}
    return {"success": False, "message": "Supplier not found"}

# =========================================================================
# DEPARTMENTS, COST CENTRES, BUDGETS, APPROVERS & WAREHOUSES
# =========================================================================
@router.get("/departments")
def get_departments(request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    data = filter_by_user_or_company(db.get("departments", []), email, company, role)
    return {"success": True, "data": data}

@router.get("/departments/{dept_id}")
def get_department_by_id(dept_id: str):
    target = unquote(dept_id).strip().lower()
    dept = next((d for d in db["departments"] if str(d.get("id", "")).lower() == target or str(d.get("code", "")).lower() == target), None)
    if dept:
        return {"success": True, "data": dept}
    return {"success": False, "message": "Department not found"}

@router.get("/departments/{dept_id}/budget")
def get_department_budget(dept_id: str):
    target = unquote(dept_id).strip().lower()
    dept = next((d for d in db["departments"] if str(d.get("id", "")).lower() == target or str(d.get("code", "")).lower() == target), {})
    annual = float(dept.get("budget_annual", 2400000))
    monthly = float(dept.get("budget_monthly", annual / 12))
    quarterly = float(dept.get("budget_quarterly", annual / 4))
    consumed = float(dept.get("ytd_consumption", 1850000))
    remaining = max(0, annual - consumed)
    
    return {
        "success": True,
        "data": {
            "department_id": dept.get("id"),
            "department_name": dept.get("name"),
            "cost_centre": dept.get("cost_centre", "IT-001"),
            "budget_monthly": monthly,
            "budget_quarterly": quarterly,
            "budget_annual": annual,
            "category_budgets": dept.get("category_budgets", {
                "cat-01": 1200000,
                "cat-02": 500000,
                "cat-03": 400000,
                "cat-04": 300000
            }),
            "budget_control_rule": dept.get("budget_control_rule", "Warn when budget is exceeded"),
            "ytd_consumption": consumed,
            "remaining_budget": remaining
        }
    }

@router.get("/departments/{dept_id}/consumption")
def get_department_consumption(dept_id: str):
    target = unquote(dept_id).strip().lower()
    dept = next((d for d in db["departments"] if str(d.get("id", "")).lower() == target or str(d.get("code", "")).lower() == target), {})
    return {
        "success": True,
        "data": {
            "department_id": dept.get("id"),
            "department_name": dept.get("name"),
            "cost_centre": dept.get("cost_centre", "IT-001"),
            "monthly_breakdown": [
                {"month": "2026-04", "consumed_value": 180000, "budget": 200000},
                {"month": "2026-05", "consumed_value": 210000, "budget": 200000},
                {"month": "2026-06", "consumed_value": 195000, "budget": 200000},
                {"month": "2026-07", "consumed_value": 240000, "budget": 200000},
                {"month": "2026-08", "consumed_value": 165000, "budget": 200000}
            ]
        }
    }

@router.post("/departments")
def create_department(payload: dict, request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, None)
    new_id = f"dept-{str(len(db['departments']) + 1).zfill(2)}"
    new_dept = {
        "id": new_id,
        "code": payload.get("code") or f"DEPT-0{len(db['departments'])+1}",
        "name": payload.get("name", "New Dept"),
        "company_name": company,
        "created_by": email,
        "is_sample": False,
        "head_name": payload.get("head_name", "Dr. Ananya Roy"),
        "cost_centre": payload.get("cost_centre", "IT-001"),
        "default_approver": payload.get("default_approver", "Sarah Jenkins"),
        "branch": payload.get("branch", "Main Campus - Bangalore"),
        "budget_monthly": float(payload.get("budget_monthly", 200000)),
        "budget_quarterly": float(payload.get("budget_quarterly", 600000)),
        "budget_annual": float(payload.get("budget_annual", 2400000)),
        "category_budgets": payload.get("category_budgets", {
            "cat-01": 1200000,
            "cat-02": 500000,
            "cat-03": 400000,
            "cat-04": 300000
        }),
        "budget_control_rule": payload.get("budget_control_rule", "Warn when the budget is exceeded"),
        "active_status": payload.get("active_status", True),
        "ytd_consumption": 0
    }
    db["departments"].append(new_dept)
    save_db("departments")
    return {"success": True, "data": new_dept}

@router.put("/departments/{dept_id}")
def update_department(dept_id: str, payload: dict):
    target = unquote(dept_id).strip().lower()
    for idx, d in enumerate(db["departments"]):
        if str(d.get("id", "")).strip().lower() == target or str(d.get("code", "")).strip().lower() == target:
            db["departments"][idx].update(payload)
            save_db("departments")
            return {"success": True, "data": db["departments"][idx]}
    return {"success": False, "message": "Department not found"}

@router.delete("/departments/{dept_id}")
def delete_department(dept_id: str):
    target = unquote(dept_id).strip().lower()
    initial_count = len(db["departments"])
    db["departments"] = [
        d for d in db["departments"]
        if str(d.get("id", "")).strip().lower() != target
        and str(d.get("code", "")).strip().lower() != target
    ]
    if len(db["departments"]) < initial_count:
        save_db("departments")
        return {"success": True, "message": "Department deleted successfully"}
    return {"success": False, "message": "Department not found"}

@router.get("/cost-centres")
def get_cost_centres(request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    scoped = filter_by_user_or_company(db.get("departments", []), email, company, role)
    result = [
        {"cost_centre_code": d.get("cost_centre"), "department_name": d.get("name"), "department_code": d.get("code"), "head_name": d.get("head_name")}
        for d in scoped
    ]
    return {"success": True, "data": result}

@router.get("/department-budgets")
def get_department_budgets(request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    scoped = filter_by_user_or_company(db.get("departments", []), email, company, role)
    result = [
        {
            "department_id": d.get("id"),
            "department_code": d.get("code"),
            "department_name": d.get("name"),
            "cost_centre": d.get("cost_centre"),
            "budget_monthly": d.get("budget_monthly", 200000),
            "budget_quarterly": d.get("budget_quarterly", 600000),
            "budget_annual": d.get("budget_annual", 2400000),
            "budget_control_rule": d.get("budget_control_rule", "Warn when the budget is exceeded")
        }
        for d in scoped
    ]
    return {"success": True, "data": result}

@router.get("/department-approvers")
def get_department_approvers(request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    scoped = filter_by_user_or_company(db.get("departments", []), email, company, role)
    result = [
        {
            "department_id": d.get("id"),
            "department_name": d.get("name"),
            "head_name": d.get("head_name", "Dr. Ananya Roy"),
            "default_approver": d.get("default_approver", "Sarah Jenkins")
        }
        for d in scoped
    ]
    return {"success": True, "data": result}

# =========================================================================
# WAREHOUSES MASTER (Code, Name, Address, Manager, Branch, Type, Active Status)
# =========================================================================
@router.get("/warehouses")
def get_warehouses(request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    data = filter_by_user_or_company(db.get("warehouses", []), email, company, role)
    return {"success": True, "data": data}

@router.get("/warehouses/{wh_id}")
def get_warehouse_by_id(wh_id: str):
    target = unquote(wh_id).strip().lower()
    wh = next((w for w in db["warehouses"] if str(w.get("id", "")).lower() == target or str(w.get("code", "")).lower() == target), None)
    if wh:
        return {"success": True, "data": wh}
    return {"success": False, "message": "Warehouse not found"}

@router.post("/warehouses")
def create_warehouse(payload: dict, request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, None)
    new_id = payload.get("id") or f"wh-{str(len(db['warehouses']) + 1).zfill(2)}"
    new_wh = {
        "id": new_id,
        "code": payload.get("code") or f"WH-0{len(db['warehouses'])+1}",
        "name": payload.get("name", "New Warehouse"),
        "company_name": company,
        "created_by": email,
        "is_sample": False,
        "address": payload.get("address", "Site Location"),
        "manager_name": payload.get("manager_name", "Store Manager"),
        "branch": payload.get("branch", "Main Campus"),
        "warehouse_type": payload.get("warehouse_type", "Central Goods Store"),
        "capacity_sqft": float(payload.get("capacity_sqft", 5000)),
        "active_status": payload.get("active_status", True),
        "total_bins": payload.get("total_bins", 10),
        "occupied_bins": payload.get("occupied_bins", 2)
    }
    db["warehouses"].append(new_wh)
    save_db("warehouses")
    return {"success": True, "data": new_wh}

@router.put("/warehouses/{wh_id}")
def update_warehouse(wh_id: str, payload: dict):
    target = unquote(wh_id).strip().lower()
    for idx, w in enumerate(db["warehouses"]):
        if str(w.get("id", "")).strip().lower() == target or str(w.get("code", "")).strip().lower() == target:
            db["warehouses"][idx].update(payload)
            save_db("warehouses")
            return {"success": True, "data": db["warehouses"][idx]}
    return {"success": False, "message": "Warehouse not found"}

@router.delete("/warehouses/{wh_id}")
def delete_warehouse(wh_id: str):
    target = unquote(wh_id).strip().lower()
    initial_count = len(db["warehouses"])
    db["warehouses"] = [
        w for w in db["warehouses"]
        if str(w.get("id", "")).strip().lower() != target
        and str(w.get("code", "")).strip().lower() != target
    ]
    if len(db["warehouses"]) < initial_count:
        save_db("warehouses")
        return {"success": True, "message": "Warehouse deleted successfully"}
    return {"success": False, "message": "Warehouse not found"}

# =========================================================================
# LOCATION LEVELS (Warehouse -> Zone -> Rack -> Shelf -> Bin)
# =========================================================================
@router.get("/locations")
@router.get("/warehouse-locations")
def get_warehouse_locations(request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    data = filter_by_user_or_company(db.get("warehouse_locations", []), email, company, role)
    return {"success": True, "data": data}

@router.get("/warehouse-zones")
def get_warehouse_zones():
    zones = list({l.get("zone", "Zone A") for l in db["warehouse_locations"]})
    return {"success": True, "data": [{"zone_name": z} for z in zones]}

@router.get("/warehouse-racks")
def get_warehouse_racks():
    racks = list({l.get("rack", "Rack 01") for l in db["warehouse_locations"]})
    return {"success": True, "data": [{"rack_name": r} for r in racks]}

@router.get("/warehouse-shelves")
def get_warehouse_shelves():
    shelves = list({l.get("shelf", "Shelf 1") for l in db["warehouse_locations"]})
    return {"success": True, "data": [{"shelf_name": s} for s in shelves]}

@router.get("/warehouse-bins")
def get_warehouse_bins():
    bins = list({l.get("bin", "Bin 01") for l in db["warehouse_locations"]})
    return {"success": True, "data": [{"bin_name": b} for b in bins]}

@router.post("/locations")
def create_location(payload: dict, request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, None)
    new_id = f"loc-{str(len(db['warehouse_locations']) + 1).zfill(2)}"
    zone = payload.get("zone", "Zone A")
    rack = payload.get("rack", "Rack 01")
    shelf = payload.get("shelf", "Shelf 1")
    bin_name = payload.get("bin", "Bin 01")
    auto_code = f"{zone.replace(' ', '')}-{rack.replace(' ', '')}-{shelf.replace(' ', '')}-{bin_name.replace(' ', '')}"
    
    new_loc = {
        "id": new_id,
        "warehouse_id": payload.get("warehouse_id", "wh-01"),
        "company_name": company,
        "created_by": email,
        "is_sample": False,
        "zone": zone,
        "rack": rack,
        "shelf": shelf,
        "bin": bin_name,
        "code": payload.get("code") or auto_code,
        "active_status": payload.get("active_status", True)
    }
    db["warehouse_locations"].append(new_loc)
    save_db("warehouse_locations")
    return {"success": True, "data": new_loc}

@router.put("/locations/{loc_id}")
def update_location(loc_id: str, payload: dict):
    target = unquote(loc_id).strip().lower()
    for idx, l in enumerate(db["warehouse_locations"]):
        if str(l.get("id", "")).strip().lower() == target or str(l.get("code", "")).strip().lower() == target:
            db["warehouse_locations"][idx].update(payload)
            save_db("warehouse_locations")
            return {"success": True, "data": db["warehouse_locations"][idx]}
    return {"success": False, "message": "Location bin not found"}

@router.delete("/locations/{loc_id}")
def delete_location(loc_id: str):
    target = unquote(loc_id).strip().lower()
    initial_count = len(db["warehouse_locations"])
    db["warehouse_locations"] = [
        l for l in db["warehouse_locations"]
        if str(l.get("id", "")).strip().lower() != target
        and str(l.get("code", "")).strip().lower() != target
    ]
    if len(db["warehouse_locations"]) < initial_count:
        save_db("warehouse_locations")
        return {"success": True, "message": "Location bin deleted successfully"}
    return {"success": False, "message": "Location bin not found"}

# =========================================================================
# PERFORMANCE INVENTORY BALANCES (item_id + warehouse_id + location_id + batch_id)
# =========================================================================
@router.get("/inventory-balances")
def get_inventory_balances(request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    scoped_balances = filter_by_user_or_company(db.get("inventory_balances", []), email, company, role)
    result = []
    for bal in scoped_balances:
        item = next((i for i in db["items"] if i["id"] == bal.get("item_id")), {})
        wh = next((w for w in db["warehouses"] if w["id"] == bal.get("warehouse_id")), {})
        loc = next((l for l in db["warehouse_locations"] if l["id"] == bal.get("location_id")), {})
        
        composite_key = f"{bal.get('item_id')}+{bal.get('warehouse_id')}+{bal.get('location_id')}+{bal.get('batch_id', 'DEFAULT')}"
        result.append({
            "composite_key": composite_key,
            "id": bal.get("id"),
            "item_id": bal.get("item_id"),
            "item_code": item.get("item_code", "N/A"),
            "item_name": item.get("item_name", "N/A"),
            "warehouse_id": bal.get("warehouse_id"),
            "warehouse_name": wh.get("name", "N/A"),
            "location_id": bal.get("location_id"),
            "location_code": loc.get("code", "N/A"),
            "batch_id": bal.get("batch_id", "DEFAULT"),
            "on_hand_qty": bal.get("on_hand_qty", 0),
            "reserved_qty": bal.get("reserved_qty", 0),
            "available_qty": bal.get("available_qty", 0),
            "valuation_rate": bal.get("valuation_rate", 0),
            "total_value": bal.get("available_qty", 0) * bal.get("valuation_rate", 0)
        })
    return {"success": True, "data": result}

@router.get("/roles")
def get_roles():
    return {"success": True, "data": db["roles"]}

@router.get("/permissions")
def get_permissions():
    return {"success": True, "data": db["permissions"]}

@router.get("/users")
def get_users(request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None), x_user_role: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, x_user_role)
    data = filter_by_user_or_company(db.get("users", []), email, company, role)
    return {"success": True, "data": data}

@router.post("/users")
def create_user(payload: dict, request: Request, x_user_email: str = Header(None), x_company_name: str = Header(None)):
    email, company, role = get_auth_context(request, x_user_email, x_company_name, None)
    new_id = f"usr-{str(len(db['users']) + 1).zfill(2)}"
    new_u = {
        "id": new_id,
        "name": payload.get("name", "New User"),
        "email": payload.get("email", "user@company.com"),
        "company_name": company or payload.get("company_name", "Organization"),
        "created_by": email,
        "is_sample": False,
        "emp_code": payload.get("emp_code") or f"EMP-0{len(db['users'])+1}",
        "role_id": payload.get("role_id", "role-requester"),
        "department_id": payload.get("department_id", "dept-01"),
        "branch_id": "br-01",
        "is_active": True
    }
    db["users"].append(new_u)
    save_db("users")
    return {"success": True, "data": new_u}

@router.put("/users/{user_id}")
def update_user(user_id: str, payload: dict):
    target = unquote(user_id).strip().lower()
    for idx, u in enumerate(db["users"]):
        if str(u.get("id", "")).strip().lower() == target or str(u.get("emp_code", "")).strip().lower() == target:
            db["users"][idx].update(payload)
            save_db("users")
            return {"success": True, "data": db["users"][idx]}
    return {"success": False, "message": "User not found"}

@router.delete("/users/{user_id}")
def delete_user(user_id: str):
    target = unquote(user_id).strip().lower()
    initial_count = len(db["users"])
    db["users"] = [
        u for u in db["users"]
        if str(u.get("id", "")).strip().lower() != target
        and str(u.get("emp_code", "")).strip().lower() != target
    ]
    if len(db["users"]) < initial_count:
        save_db("users")
        return {"success": True, "message": "User deleted successfully"}
    return {"success": False, "message": "User not found"}

