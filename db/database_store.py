import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'inventory_store.json')

db = {
    "users": [],
    "roles": [],
    "permissions": [],
    "role_permissions": [],
    "departments": [],
    "cost_centres": [],
    "warehouses": [],
    "warehouse_locations": [],
    "item_categories": [],
    "brands": [],
    "units_of_measure": [],
    "unit_conversions": [],
    "tax_rates": [],
    "items": [],
    "item_batches": [],
    "item_serials": [],
    "suppliers": [],
    "supplier_contacts": [],
    "supplier_bank_accounts": [],
    "indents": [],
    "indent_items": [],
    "approval_workflows": [],
    "approval_requests": [],
    "rfqs": [],
    "rfq_items": [],
    "rfq_suppliers": [],
    "quotations": [],
    "quotation_items": [],
    "purchase_orders": [],
    "po_items": [],
    "goods_receipts": [],
    "grn_items": [],
    "quality_inspections": [],
    "inventory_ledger": [],
    "inventory_balances": [],
    "stock_issues": [],
    "stock_issue_items": [],
    "stock_returns": [],
    "supplier_returns": [],
    "stock_transfers": [],
    "stock_transfer_items": [],
    "stock_adjustments": [],
    "stock_count_sessions": [],
    "stock_count_entries": [],
    "stock_reservations": [],
    "assets": [],
    "notifications": [],
    "audit_logs": [],
    "settings": {}
}

def save_db():
    try:
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    except Exception as err:
        print("Failed to save database file:", err)

def load_db():
    global db
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                db.update(loaded)
        else:
            seed_initial_data()
            save_db()
    except Exception as err:
        print("Failed to load database file, initializing seed:", err)
        seed_initial_data()
        save_db()
    return db

def seed_initial_data():
    print("Seeding initial Python FastAPI database...")
    now = datetime.now().isoformat()

    db["settings"] = {
        "company_name": "Apex Enterprises Pvt Ltd",
        "company_logo": "https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=100&auto=format&fit=crop&q=60",
        "address": "100 Industrial Park, Zone 4, Bangalore, India",
        "tax_number": "29AAAAA0000A1Z5",
        "contact_email": "support@apexenterprises.com",
        "financial_year": "2026-2027",
        "allow_negative_stock": False,
        "valuation_method": "FIFO",
        "default_warehouse_id": "wh-01",
        "expiry_warning_days": 30,
        "decimal_precision_qty": 2,
        "decimal_precision_currency": 2,
        "numbering_series": {
            "IND": 1001,
            "RFQ": 2001,
            "PO": 3001,
            "GRN": 4001,
            "ISS": 5001,
            "TRN": 6001,
            "ADJ": 7001
        }
    }

    db["roles"] = [
        {"id": "role-admin", "name": "Super Administrator", "description": "Full system access & workflow configuration"},
        {"id": "role-purchase", "name": "Purchase Manager", "description": "Manage RFQs, Supplier Quotes, POs & Supplier Ratings"},
        {"id": "role-store", "name": "Store Manager", "description": "Manage GRN, Stock Issues, Transfers, Returns & Audits"},
        {"id": "role-dept-mgr", "name": "Department Manager", "description": "Approve department indents & view consumption budgets"},
        {"id": "role-requester", "name": "Employee / Requester", "description": "Create material indents & track requests"},
        {"id": "role-finance", "name": "Finance User", "description": "Review PO values, tax verification & financial approvals"},
        {"id": "role-auditor", "name": "Auditor", "description": "Read-only access to audit logs, stock ledger & reports"}
    ]

    db["permissions"] = [
        "item.view", "item.create", "item.edit", "item.delete",
        "supplier.view", "supplier.create", "supplier.edit",
        "indent.create", "indent.view", "indent.approve", "indent.cancel",
        "rfq.create", "rfq.view", "rfq.send",
        "quote.create", "quote.compare", "quote.select",
        "po.create", "po.approve", "po.print",
        "grn.create", "grn.inspect", "grn.post",
        "stock.view", "stock.issue", "stock.return", "stock.transfer", "stock.adjust", "stock.verify",
        "asset.view", "asset.assign",
        "report.view", "report.export",
        "audit.view", "settings.edit"
    ]

    db["users"] = [
        {"id": "usr-01", "name": "Sarah Jenkins", "email": "admin@company.com", "password": "password123", "role_id": "role-admin", "emp_code": "EMP-001", "department_id": "dept-01", "branch_id": "br-01", "is_active": True},
        {"id": "usr-02", "name": "Rajesh Kumar", "email": "purchase@company.com", "password": "password123", "role_id": "role-purchase", "emp_code": "EMP-002", "department_id": "dept-02", "branch_id": "br-01", "is_active": True},
        {"id": "usr-03", "name": "Michael Chang", "email": "store@company.com", "password": "password123", "role_id": "role-store", "emp_code": "EMP-003", "department_id": "dept-03", "branch_id": "br-01", "is_active": True},
        {"id": "usr-04", "name": "Dr. Ananya Roy", "email": "deptmgr@company.com", "password": "password123", "role_id": "role-dept-mgr", "emp_code": "EMP-004", "department_id": "dept-01", "branch_id": "br-01", "is_active": True},
        {"id": "usr-05", "name": "David Miller", "email": "requester@company.com", "password": "password123", "role_id": "role-requester", "emp_code": "EMP-005", "department_id": "dept-01", "branch_id": "br-01", "is_active": True},
        {"id": "usr-06", "name": "Priya Sharma", "email": "finance@company.com", "password": "password123", "role_id": "role-finance", "emp_code": "EMP-006", "department_id": "dept-04", "branch_id": "br-01", "is_active": True},
        {"id": "usr-07", "name": "Robert Wilson", "email": "auditor@company.com", "password": "password123", "role_id": "role-auditor", "emp_code": "EMP-007", "department_id": "dept-04", "branch_id": "br-01", "is_active": True}
    ]

    db["departments"] = [
        {"id": "dept-01", "code": "IT-DEPT", "name": "Information Technology", "head_id": "usr-04", "cost_centre": "IT-001", "budget_annual": 2500000, "active_status": True},
        {"id": "dept-02", "code": "PUR-DEPT", "name": "Procurement & Purchasing", "head_id": "usr-02", "cost_centre": "PUR-002", "budget_annual": 1500000, "active_status": True},
        {"id": "dept-03", "code": "WH-DEPT", "name": "Warehouse & Stores Operations", "head_id": "usr-03", "cost_centre": "STR-003", "budget_annual": 1000000, "active_status": True},
        {"id": "dept-04", "code": "FIN-DEPT", "name": "Finance & Accounts", "head_id": "usr-06", "cost_centre": "FIN-004", "budget_annual": 800000, "active_status": True},
        {"id": "dept-05", "code": "MNT-DEPT", "name": "Maintenance & Engineering", "head_id": "usr-01", "cost_centre": "MNT-005", "budget_annual": 1800000, "active_status": True}
    ]

    db["warehouses"] = [
        {"id": "wh-01", "code": "WH-MAIN", "name": "Central Goods Warehouse", "address": "Plot 12, Industrial Hub", "manager_id": "usr-03", "active_status": True},
        {"id": "wh-02", "code": "WH-SUB1", "name": "IT Assets & Electronics Store", "address": "Building B, Floor 2", "manager_id": "usr-03", "active_status": True},
        {"id": "wh-03", "code": "WH-TRANS", "name": "Transit & Quarantine Store", "address": "Receiving Bay 1", "manager_id": "usr-03", "active_status": True}
    ]

    db["warehouse_locations"] = [
        {"id": "loc-01", "warehouse_id": "wh-01", "zone": "Zone A", "rack": "Rack 01", "shelf": "Shelf 2", "bin": "Bin 05", "code": "A-R01-S2-B05"},
        {"id": "loc-02", "warehouse_id": "wh-01", "zone": "Zone A", "rack": "Rack 02", "shelf": "Shelf 1", "bin": "Bin 12", "code": "A-R02-S1-B12"},
        {"id": "loc-03", "warehouse_id": "wh-02", "zone": "Zone IT", "rack": "Rack IT-1", "shelf": "Shelf Top", "bin": "Bin SEC-1", "code": "IT-R1-ST-B1"}
    ]

    db["item_categories"] = [
        {"id": "cat-01", "category_code": "IT", "category_name": "IT Equipment", "description": "Laptops, Desktops, Peripherals", "is_active": True},
        {"id": "cat-02", "category_code": "ELE", "category_name": "Electrical & Hardware", "description": "Cables, Switches, Power Supplies", "is_active": True},
        {"id": "cat-03", "category_code": "OFF", "category_name": "Office Supplies & Stationery", "description": "Paper, Pens, Cartridges", "is_active": True},
        {"id": "cat-04", "category_code": "RAW", "category_name": "Raw Materials", "description": "Steel, Aluminium, Chemicals", "is_active": True}
    ]

    db["brands"] = [
        {"id": "brd-01", "brand_name": "Dell Technologies"},
        {"id": "brd-02", "brand_name": "HP Enterprise"},
        {"id": "brd-03", "brand_name": "Schneider Electric"},
        {"id": "brd-04", "brand_name": "3M Industrial"}
    ]

    db["units_of_measure"] = [
        {"id": "uom-01", "unit_name": "Pieces", "unit_symbol": "Pcs", "decimal_allowed": False},
        {"id": "uom-02", "unit_name": "Box of 20", "unit_symbol": "Box", "decimal_allowed": False},
        {"id": "uom-03", "unit_name": "Kilograms", "unit_symbol": "Kg", "decimal_allowed": True},
        {"id": "uom-04", "unit_name": "Meters", "unit_symbol": "Mtr", "decimal_allowed": True},
        {"id": "uom-05", "unit_name": "Liters", "unit_symbol": "Ltr", "decimal_allowed": True}
    ]

    db["tax_rates"] = [
        {"id": "tax-0", "name": "Exempt (0%)", "percentage": 0, "tax_type": "GST_0"},
        {"id": "tax-5", "name": "GST 5%", "percentage": 5, "tax_type": "GST_5"},
        {"id": "tax-12", "name": "GST 12%", "percentage": 12, "tax_type": "GST_12"},
        {"id": "tax-18", "name": "GST 18%", "percentage": 18, "tax_type": "GST_18"},
        {"id": "tax-28", "name": "GST 28%", "percentage": 28, "tax_type": "GST_28"}
    ]

    db["items"] = [
        {
            "id": "itm-01",
            "item_code": "IT-LAP-0001",
            "item_name": "Dell Latitude 5440 Laptop",
            "description": "Intel i7 13th Gen, 16GB RAM, 512GB SSD, 14-inch Display",
            "category_id": "cat-01",
            "brand_id": "brd-01",
            "uom_id": "uom-01",
            "purchase_uom_id": "uom-01",
            "tax_rate_id": "tax-18",
            "hsn_sac_code": "84713010",
            "min_stock_level": 5,
            "max_stock_level": 50,
            "reorder_level": 10,
            "reorder_qty": 15,
            "valuation_rate": 72000,
            "default_location_id": "loc-03",
            "is_batch_tracked": False,
            "is_serial_tracked": True,
            "is_expiry_tracked": False,
            "barcode": "8901234567891",
            "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=300&auto=format&fit=crop&q=60",
            "is_active": True,
            "created_at": now
        },
        {
            "id": "itm-02",
            "item_code": "ELE-CBL-0002",
            "item_name": "Cat6 Ethernet Cable (305m Drum)",
            "description": "High speed Gigabit Shielded Copper Cable Drum",
            "category_id": "cat-02",
            "brand_id": "brd-03",
            "uom_id": "uom-04",
            "purchase_uom_id": "uom-04",
            "tax_rate_id": "tax-18",
            "hsn_sac_code": "85444999",
            "min_stock_level": 100,
            "max_stock_level": 1000,
            "reorder_level": 300,
            "reorder_qty": 500,
            "valuation_rate": 45,
            "default_location_id": "loc-01",
            "is_batch_tracked": True,
            "is_serial_tracked": False,
            "is_expiry_tracked": False,
            "barcode": "8901234567892",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&auto=format&fit=crop&q=60",
            "is_active": True,
            "created_at": now
        },
        {
            "id": "itm-03",
            "item_code": "OFF-PPR-0003",
            "item_name": "A4 Copy Paper 80GSM (Rim)",
            "description": "High brightness multi-purpose printing paper",
            "category_id": "cat-03",
            "brand_id": "brd-04",
            "uom_id": "uom-01",
            "purchase_uom_id": "uom-02",
            "tax_rate_id": "tax-12",
            "hsn_sac_code": "48025610",
            "min_stock_level": 20,
            "max_stock_level": 200,
            "reorder_level": 50,
            "reorder_qty": 100,
            "valuation_rate": 280,
            "default_location_id": "loc-02",
            "is_batch_tracked": False,
            "is_serial_tracked": False,
            "is_expiry_tracked": False,
            "barcode": "8901234567893",
            "image_url": "https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=300&auto=format&fit=crop&q=60",
            "is_active": True,
            "created_at": now
        },
        {
            "id": "itm-04",
            "item_code": "RAW-CHM-0004",
            "item_name": "Industrial Cleaning Solvent C-40",
            "description": "High purity solvent for electronic component washing",
            "category_id": "cat-04",
            "brand_id": "brd-04",
            "uom_id": "uom-05",
            "purchase_uom_id": "uom-05",
            "tax_rate_id": "tax-18",
            "hsn_sac_code": "38140010",
            "min_stock_level": 50,
            "max_stock_level": 500,
            "reorder_level": 150,
            "reorder_qty": 200,
            "valuation_rate": 350,
            "default_location_id": "loc-01",
            "is_batch_tracked": True,
            "is_serial_tracked": False,
            "is_expiry_tracked": True,
            "barcode": "8901234567894",
            "image_url": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=300&auto=format&fit=crop&q=60",
            "is_active": True,
            "created_at": now
        }
    ]

    db["suppliers"] = [
        {
            "id": "sup-01",
            "supplier_code": "SUP-00045",
            "supplier_name": "Infotech Systems Ltd",
            "contact_person": "Vikram Malhotra",
            "phone": "+91 98765 43210",
            "email": "sales@infotechsystems.com",
            "address_registered": "45 Technology Park, Whitefield, Bangalore",
            "address_billing": "45 Technology Park, Whitefield, Bangalore",
            "gst_number": "29AAACI1234F1Z9",
            "pan_number": "AAACI1234F",
            "payment_terms": "Net 30 days",
            "delivery_lead_time_days": 5,
            "rating": 4.8,
            "approval_status": "Approved",
            "is_active": True
        },
        {
            "id": "sup-02",
            "supplier_code": "SUP-00046",
            "supplier_name": "Apex Electrical Controls",
            "contact_person": "Suresh Menon",
            "phone": "+91 98450 11223",
            "email": "orders@apexelectrical.com",
            "address_registered": "78 Industrial Estate, Peenya, Bangalore",
            "address_billing": "78 Industrial Estate, Peenya, Bangalore",
            "gst_number": "29AAACE9876K1Z1",
            "pan_number": "AAACE9876K",
            "payment_terms": "Net 15 days",
            "delivery_lead_time_days": 3,
            "rating": 4.5,
            "approval_status": "Approved",
            "is_active": True
        }
    ]

    db["inventory_balances"] = [
        {"id": "bal-01", "item_id": "itm-01", "warehouse_id": "wh-02", "location_id": "loc-03", "on_hand_qty": 8, "reserved_qty": 3, "available_qty": 5, "valuation_rate": 72000},
        {"id": "bal-02", "item_id": "itm-02", "warehouse_id": "wh-01", "location_id": "loc-01", "on_hand_qty": 650, "reserved_qty": 50, "available_qty": 600, "valuation_rate": 45},
        {"id": "bal-03", "item_id": "itm-03", "warehouse_id": "wh-01", "location_id": "loc-02", "on_hand_qty": 18, "reserved_qty": 0, "available_qty": 18, "valuation_rate": 280},
        {"id": "bal-04", "item_id": "itm-04", "warehouse_id": "wh-01", "location_id": "loc-01", "on_hand_qty": 120, "reserved_qty": 0, "available_qty": 120, "valuation_rate": 350}
    ]

    db["indents"] = [
        {
            "id": "ind-1001",
            "indent_number": "IND-2026-001001",
            "request_date": "2026-08-08",
            "department_id": "dept-01",
            "requested_by": "usr-05",
            "required_date": "2026-08-25",
            "purpose": "New Developer Onboarding Setup",
            "priority": "High",
            "cost_centre": "IT-001",
            "remarks": "Urgent laptops for new engineering team hires",
            "status": "Submitted",
            "total_estimated_amount": 1440000,
            "created_at": now
        }
    ]

    db["audit_logs"] = [
        {
            "id": "aud-01",
            "user_id": "usr-01",
            "action": "SYSTEM_INIT",
            "module": "SYSTEM",
            "record_id": "SYS-001",
            "details": "Standalone Python FastAPI Database seeded successfully",
            "timestamp": now,
            "ip_address": "127.0.0.1"
        }
    ]

    print("Standalone Python FastAPI Seed complete.")

def get_next_doc_number(doc_type: str) -> str:
    if "numbering_series" not in db["settings"]:
        db["settings"]["numbering_series"] = {}
    
    curr = db["settings"]["numbering_series"].get(doc_type, 1000)
    next_val = curr + 1
    db["settings"]["numbering_series"][doc_type] = next_val
    save_db()
    
    year = datetime.now().year
    return f"{doc_type}-{year}-{str(next_val).zfill(6)}"

# Load database on import
load_db()
