from fastapi import APIRouter
from db.database_store import db, save_db
from schemas.schemas import ItemCreate, SupplierCreate
from datetime import datetime
from urllib.parse import unquote
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["Masters"])

# =========================================================================
# ITEMS MASTER & ALIASES
# =========================================================================
@router.get("/items")
def get_items():
    return {"success": True, "data": db["items"]}

@router.get("/items/search")
def search_items(q: str = ""):
    query = q.lower().strip()
    filtered = [
        i for i in db["items"]
        if query in i.get("item_code", "").lower() or query in i.get("item_name", "").lower()
    ]
    return {"success": True, "data": filtered}

@router.post("/items/import")
def import_items(payload: Dict[str, Any]):
    rows = payload.get("rows", [])
    count = 0
    for r in rows:
        if r.get("item_code") and r.get("item_name"):
            new_id = f"itm-{len(db['items']) + 1}"
            db["items"].append({
                "id": new_id,
                "item_code": r.get("item_code"),
                "item_name": r.get("item_name"),
                "valuation_rate": float(r.get("valuation_rate", 1000)),
                "category_id": "cat-01",
                "uom_id": "uom-01",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            })
            count += 1
    save_db()
    return {"success": True, "message": f"Successfully imported {count} items."}

@router.get("/items/export")
def export_items():
    return {"success": True, "data": db["items"]}

@router.get("/items/{item_id}")
def get_single_item(item_id: str):
    target = unquote(item_id).strip().lower()
    item = next((i for i in db["items"] if str(i.get("id", "")).lower() == target or str(i.get("item_code", "")).lower() == target), None)
    if item:
        return {"success": True, "data": item}
    return {"success": False, "message": "Item not found"}

@router.post("/items")
def create_item(item: ItemCreate):
    new_id = f"itm-{str(len(db['items']) + 1).zfill(2)}"
    item_code = item.item_code or f"ITM-{datetime.now().strftime('%Y%m%d')}-{len(db['items']) + 1}"
    
    new_item = {
        "id": new_id,
        "item_code": item_code,
        "item_name": item.item_name,
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
        "valuation_rate": item.valuation_rate or 1000
    }
    db["inventory_balances"].append(balance_record)
    save_db()

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

@router.get("/brands")
def get_brands():
    return {"success": True, "data": db["brands"]}

@router.get("/uom")
@router.get("/uoms")
@router.get("/units-of-measure")
def get_uom():
    return {"success": True, "data": db["units_of_measure"]}

@router.get("/taxes")
@router.get("/tax-rates")
def get_tax_rates():
    return {"success": True, "data": db["tax_rates"]}

# =========================================================================
# SUPPLIERS MASTER
# =========================================================================
@router.get("/suppliers")
def get_suppliers():
    return {"success": True, "data": db["suppliers"]}

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
def create_supplier(sup: SupplierCreate):
    new_id = f"sup-{str(len(db['suppliers']) + 1).zfill(2)}"
    sup_code = sup.supplier_code or f"SUP-{str(len(db['suppliers']) + 48).zfill(5)}"
    
    new_supplier = {
        "id": new_id,
        "supplier_code": sup_code,
        "supplier_name": sup.supplier_name,
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
    save_db()
    return {"success": True, "data": new_supplier}

@router.put("/suppliers/{supplier_id}")
def update_supplier(supplier_id: str, payload: dict):
    target = unquote(supplier_id).strip().lower()
    for idx, s in enumerate(db["suppliers"]):
        if str(s.get("id", "")).strip().lower() == target or str(s.get("supplier_code", "")).strip().lower() == target:
            db["suppliers"][idx].update(payload)
            save_db()
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
        save_db()
        return {"success": True, "message": "Supplier deleted successfully"}
    return {"success": False, "message": "Supplier not found"}

# =========================================================================
# DEPARTMENTS, WAREHOUSES, LOCATIONS, USERS & PERMISSIONS
# =========================================================================
@router.get("/departments")
def get_departments():
    return {"success": True, "data": db["departments"]}

@router.get("/departments/{dept_id}/budget")
def get_department_budget(dept_id: str):
    dept = next((d for d in db["departments"] if d["id"] == dept_id), {})
    return {"success": True, "data": {"annual_budget": dept.get("budget_annual", 1500000), "utilized": 450000, "remaining": 1050000}}

@router.get("/departments/{dept_id}/consumption")
def get_department_consumption(dept_id: str):
    return {"success": True, "data": [{"month": "2026-08", "consumed_value": 85000}]}

@router.post("/departments")
def create_department(payload: dict):
    new_id = f"dept-{str(len(db['departments']) + 1).zfill(2)}"
    new_dept = {
        "id": new_id,
        "code": payload.get("code") or f"DEPT-{len(db['departments'])+1}",
        "name": payload.get("name", "New Dept"),
        "head_id": payload.get("head_id", "usr-04"),
        "cost_centre": payload.get("cost_centre", "CC-001"),
        "budget_annual": float(payload.get("budget_annual", 1000000)),
        "active_status": True
    }
    db["departments"].append(new_dept)
    save_db()
    return {"success": True, "data": new_dept}

@router.get("/warehouses")
def get_warehouses():
    return {"success": True, "data": db["warehouses"]}

@router.post("/warehouses")
def create_warehouse(payload: dict):
    new_id = f"wh-{str(len(db['warehouses']) + 1).zfill(2)}"
    new_wh = {
        "id": new_id,
        "code": payload.get("code") or f"WH-0{len(db['warehouses'])+1}",
        "name": payload.get("name", "New Warehouse"),
        "address": payload.get("address", "Site Location"),
        "manager_id": payload.get("manager_id", "usr-03"),
        "active_status": True
    }
    db["warehouses"].append(new_wh)
    save_db()
    return {"success": True, "data": new_wh}

@router.get("/locations")
@router.get("/warehouse-locations")
def get_warehouse_locations():
    return {"success": True, "data": db["warehouse_locations"]}

@router.post("/locations")
def create_location(payload: dict):
    new_id = f"loc-{str(len(db['warehouse_locations']) + 1).zfill(2)}"
    new_loc = {
        "id": new_id,
        "warehouse_id": payload.get("warehouse_id", "wh-01"),
        "zone": payload.get("zone", "Zone A"),
        "rack": payload.get("rack", "Rack 1"),
        "shelf": payload.get("shelf", "Shelf 1"),
        "bin": payload.get("bin", "Bin 1"),
        "code": payload.get("code") or f"LOC-0{len(db['warehouse_locations'])+1}"
    }
    db["warehouse_locations"].append(new_loc)
    save_db()
    return {"success": True, "data": new_loc}

@router.get("/roles")
def get_roles():
    return {"success": True, "data": db["roles"]}

@router.get("/permissions")
def get_permissions():
    return {"success": True, "data": db["permissions"]}

@router.get("/users")
def get_users():
    return {"success": True, "data": db["users"]}

@router.post("/users")
def create_user(payload: dict):
    new_id = f"usr-{str(len(db['users']) + 1).zfill(2)}"
    new_u = {
        "id": new_id,
        "name": payload.get("name", "New User"),
        "email": payload.get("email", "user@company.com"),
        "emp_code": payload.get("emp_code") or f"EMP-0{len(db['users'])+1}",
        "role_id": payload.get("role_id", "role-requester"),
        "department_id": payload.get("department_id", "dept-01"),
        "branch_id": "br-01",
        "is_active": True
    }
    db["users"].append(new_u)
    save_db()
    return {"success": True, "data": new_u}

@router.put("/users/{user_id}")
def update_user(user_id: str, payload: dict):
    target = unquote(user_id).strip().lower()
    for idx, u in enumerate(db["users"]):
        if str(u.get("id", "")).strip().lower() == target or str(u.get("emp_code", "")).strip().lower() == target:
            db["users"][idx].update(payload)
            save_db()
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
        save_db()
        return {"success": True, "message": "User deleted successfully"}
    return {"success": False, "message": "User not found"}
