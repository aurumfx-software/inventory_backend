from fastapi import APIRouter
from db.database_store import db, save_db
from schemas.schemas import ItemCreate, SupplierCreate
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Masters"])

# Items Master
@router.get("/items")
def get_items():
    return {"success": True, "data": db["items"]}

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

@router.get("/item-categories")
def get_categories():
    return {"success": True, "data": db["item_categories"]}

@router.get("/brands")
def get_brands():
    return {"success": True, "data": db["brands"]}

@router.get("/uom")
@router.get("/units-of-measure")
def get_uom():
    return {"success": True, "data": db["units_of_measure"]}

@router.get("/tax-rates")
def get_tax_rates():
    return {"success": True, "data": db["tax_rates"]}

@router.get("/suppliers")
def get_suppliers():
    return {"success": True, "data": db["suppliers"]}

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

@router.get("/departments")
def get_departments():
    return {"success": True, "data": db["departments"]}

@router.get("/warehouses")
def get_warehouses():
    return {"success": True, "data": db["warehouses"]}

@router.get("/warehouse-locations")
def get_warehouse_locations():
    return {"success": True, "data": db["warehouse_locations"]}

@router.get("/roles")
def get_roles():
    return {"success": True, "data": db["roles"]}

@router.get("/users")
def get_users():
    return {"success": True, "data": db["users"]}

