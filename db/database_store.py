import os
import json
from datetime import datetime

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
    """Save/Persist current database state directly to PostgreSQL database tables."""
    try:
        from db.database import check_db_connection, SessionLocal, engine, Base
        from models.orm_models import TABLE_MODEL_MAP, SystemSetting

        if not check_db_connection():
            print("[DB ERROR] Cannot save: PostgreSQL database connection is offline. Check .env credentials.")
            return

        Base.metadata.create_all(bind=engine)
        session = SessionLocal()
        try:
            # Sync settings to PostgreSQL
            if "settings" in db and isinstance(db["settings"], dict):
                for key, val in db["settings"].items():
                    setting_obj = session.query(SystemSetting).filter_by(key=key).first()
                    payload_val = val if isinstance(val, (dict, list)) else {"value": val}
                    if not setting_obj:
                        setting_obj = SystemSetting(key=key, payload=payload_val)
                        session.add(setting_obj)
                    else:
                        setting_obj.payload = payload_val

            # Sync all domain tables to PostgreSQL
            for table_name, model_cls in TABLE_MODEL_MAP.items():
                records = db.get(table_name, [])
                if not isinstance(records, list):
                    continue
                for idx, item in enumerate(records):
                    if isinstance(item, dict):
                        item_id = str(item.get("id", f"{table_name}-{idx+1}"))
                        payload_val = item
                    else:
                        item_id = str(item)
                        payload_val = {"id": str(item), "name": str(item)}

                    existing = session.query(model_cls).filter_by(id=item_id).first()
                    if not existing:
                        obj = model_cls(id=item_id, payload=payload_val)
                        session.add(obj)
                    else:
                        existing.payload = payload_val
            session.commit()
            print("[DB SUCCESS] Database state saved to PostgreSQL successfully.")
        except Exception as pg_err:
            session.rollback()
            import traceback
            traceback.print_exc()
            print("[DB ERROR] Error saving to PostgreSQL database:", pg_err)
        finally:
            session.close()
    except Exception as err:
        print("[DB ERROR] Failed to connect to PostgreSQL:", err)

def load_db():
    """Load database state exclusively from PostgreSQL database tables."""
    global db

    try:
        from db.database import check_db_connection, SessionLocal, engine, Base
        from models.orm_models import TABLE_MODEL_MAP, SystemSetting

        if not check_db_connection():
            print("[DB WARN] PostgreSQL database is not accessible. Seeding in-memory state until PostgreSQL connects.")
            if not db.get("users"):
                seed_initial_data()
            return db

        Base.metadata.create_all(bind=engine)
        session = SessionLocal()
        try:
            # Load settings from PostgreSQL
            settings_rows = session.query(SystemSetting).all()
            if settings_rows:
                db["settings"] = {}
                for row in settings_rows:
                    val = row.payload
                    if isinstance(val, dict) and "value" in val and len(val) == 1:
                        db["settings"][row.key] = val["value"]
                    else:
                        db["settings"][row.key] = val

            # Load domain tables from PostgreSQL
            loaded_any = False
            for table_name, model_cls in TABLE_MODEL_MAP.items():
                rows = session.query(model_cls).all()
                if rows:
                    db[table_name] = [r.payload for r in rows if r.payload]
                    loaded_any = True

            if not loaded_any:
                print("[DB INFO] PostgreSQL database is empty. Seeding initial data directly into PostgreSQL...")
                seed_initial_data()
                save_db()
            else:
                print("[DB SUCCESS] Database state loaded strictly from PostgreSQL database.")

            return db
        except Exception as pg_load_err:
            print("[DB ERROR] Error loading from PostgreSQL:", pg_load_err)
        finally:
            session.close()
    except Exception as err:
        print("[DB ERROR] Failed PostgreSQL database load:", err)

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
            "request_date": "2026-08-18",
            "department_id": "dept-01",
            "requested_by": "usr-05",
            "required_date": "2026-08-30",
            "purpose": "New Developer Onboarding Setup",
            "priority": "High",
            "cost_centre_or_project": "IT-001",
            "cost_centre": "IT-001",
            "remarks": "Urgent laptops for new engineering team hires",
            "status": "Submitted",
            "total_estimated_amount": 1440000,
            "items": [
                {"id": "ind-item-1", "item_id": "itm-01", "item_code": "IT-LAP-0001", "item_name": "Dell Latitude 5440 Laptop", "requested_qty": 20, "approved_qty": 20, "estimated_rate": 72000, "estimated_amount": 1440000, "required_date": "2026-08-30"}
            ],
            "created_at": now
        },
        {
            "id": "ind-1002",
            "indent_number": "IND-2026-001002",
            "request_date": "2026-08-17",
            "department_id": "dept-02",
            "requested_by": "usr-03",
            "required_date": "2026-08-28",
            "purpose": "Plant Floor Maintenance Spares",
            "priority": "Normal",
            "cost_centre_or_project": "MAINT-002",
            "cost_centre": "MAINT-002",
            "remarks": "Routine cabling and maintenance materials",
            "status": "Submitted",
            "total_estimated_amount": 180000,
            "items": [
                {"id": "ind-item-2", "item_id": "itm-02", "item_code": "ELE-CBL-0002", "item_name": "Cat6 Ethernet Cable (305m Drum)", "requested_qty": 4, "approved_qty": 4, "estimated_rate": 45000, "estimated_amount": 180000, "required_date": "2026-08-28"}
            ],
            "created_at": now
        },
        {
            "id": "ind-1003",
            "indent_number": "IND-2026-001003",
            "request_date": "2026-08-15",
            "department_id": "dept-01",
            "requested_by": "usr-05",
            "required_date": "2026-08-26",
            "purpose": "Office Supplies & Printing Paper",
            "priority": "Low",
            "cost_centre_or_project": "IT-001",
            "cost_centre": "IT-001",
            "remarks": "Quarterly stationery replenishment",
            "status": "Approved",
            "total_estimated_amount": 28000,
            "items": [
                {"id": "ind-item-3", "item_id": "itm-03", "item_code": "OFF-PPR-0003", "item_name": "A4 Copy Paper 80GSM (Rim)", "requested_qty": 100, "approved_qty": 100, "estimated_rate": 280, "estimated_amount": 28000, "required_date": "2026-08-26"}
            ],
            "created_at": now
        },
        {
            "id": "ind-1004",
            "indent_number": "IND-2026-001004",
            "request_date": "2026-08-14",
            "department_id": "dept-02",
            "requested_by": "usr-03",
            "required_date": "2026-08-24",
            "purpose": "Chemical Cleaning Solvents Batch C-40",
            "priority": "Normal",
            "cost_centre_or_project": "MAINT-002",
            "cost_centre": "MAINT-002",
            "remarks": "Specify brand preferences before approval",
            "status": "Returned for correction",
            "total_estimated_amount": 70000,
            "items": [
                {"id": "ind-item-4", "item_id": "itm-04", "item_code": "RAW-CHM-0004", "item_name": "Industrial Cleaning Solvent C-40", "requested_qty": 200, "approved_qty": 200, "estimated_rate": 350, "estimated_amount": 70000, "required_date": "2026-08-24"}
            ],
            "created_at": now
        },
        {
            "id": "ind-1005",
            "indent_number": "IND-2026-001005",
            "request_date": "2026-08-12",
            "department_id": "dept-03",
            "requested_by": "usr-02",
            "required_date": "2026-08-20",
            "purpose": "Unbudgeted Executive High End Hardware",
            "priority": "Urgent",
            "priority_justification": "Executive request",
            "cost_centre_or_project": "PROD-003",
            "cost_centre": "PROD-003",
            "remarks": "Exceeds annual department budget limits",
            "status": "Rejected",
            "total_estimated_amount": 850000,
            "items": [
                {"id": "ind-item-5", "item_id": "itm-01", "item_code": "IT-LAP-0001", "item_name": "Dell Latitude 5440 Laptop", "requested_qty": 10, "approved_qty": 0, "estimated_rate": 85000, "estimated_amount": 850000, "required_date": "2026-08-20"}
            ],
            "created_at": now
        }
    ]

    db["purchase_orders"] = [
        {
            "id": "po-1001",
            "po_number": "PO-2026-001001",
            "supplier_id": "sup-01",
            "supplier_name": "Infotech Systems Ltd",
            "po_date": "2026-08-17",
            "delivery_date": "2026-08-28",
            "status": "Submitted",
            "grand_total": 360000,
            "payment_terms": "Net 30 days",
            "items": [
                {"id": "po-item-1", "item_id": "itm-01", "item_code": "IT-LAP-0001", "item_name": "Dell Latitude 5440 Laptop", "order_qty": 5, "unit_price": 72000, "total_price": 360000}
            ],
            "created_at": now
        }
    ]

    db["approval_workflows"] = [
        {
            "id": "wf-01",
            "name": "Standard High Value Indent Approval Matrix",
            "transaction_type": "INDENT",
            "department_id": "ALL",
            "branch_id": "ALL",
            "item_category_id": "ALL",
            "min_amount": 0,
            "max_amount": None,
            "urgency": "ALL",
            "steps": [
                {"step_number": 1, "step_name": "Department Manager Approval", "approver_role_id": "role-dept-mgr", "min_amount": 0, "can_change_qty": True, "can_approve_lines": True},
                {"step_number": 2, "step_name": "Store Manager Stock Check", "approver_role_id": "role-store", "min_amount": 0, "can_change_qty": True, "can_approve_lines": True},
                {"step_number": 3, "step_name": "Purchase Manager Review", "approver_role_id": "role-purchase", "min_amount": 0, "can_change_qty": True, "can_approve_lines": True},
                {"step_number": 4, "step_name": "Finance Manager Sign-off (> ₹100,000)", "approver_role_id": "role-finance", "min_amount": 100000, "can_change_qty": False, "can_approve_lines": True},
                {"step_number": 5, "step_name": "Director Approval (> ₹500,000)", "approver_role_id": "role-admin", "min_amount": 500000, "can_change_qty": False, "can_approve_lines": True}
            ]
        },
        {
            "id": "wf-02",
            "name": "Purchase Order Authorization Matrix",
            "transaction_type": "PURCHASE_ORDER",
            "department_id": "ALL",
            "branch_id": "ALL",
            "item_category_id": "ALL",
            "min_amount": 0,
            "max_amount": None,
            "urgency": "ALL",
            "steps": [
                {"step_number": 1, "step_name": "Purchase Officer Review", "approver_role_id": "role-purchase", "min_amount": 0, "can_change_qty": True, "can_approve_lines": True},
                {"step_number": 2, "step_name": "Finance Manager Sign-off", "approver_role_id": "role-finance", "min_amount": 100000, "can_change_qty": False, "can_approve_lines": True},
                {"step_number": 3, "step_name": "Managing Director Sign-off", "approver_role_id": "role-admin", "min_amount": 500000, "can_change_qty": False, "can_approve_lines": True}
            ]
        }
    ]

    db["approval_requests"] = [
        {
            "id": "app-01",
            "transaction_type": "INDENT",
            "transaction_id": "ind-1001",
            "approval_level": 1,
            "approver_id": "usr-04",
            "assigned_date": "2026-08-18T10:00:00",
            "status": "Pending",
            "comments": "Awaiting Department Manager Approval"
        },
        {
            "id": "app-02",
            "transaction_type": "PURCHASE_ORDER",
            "transaction_id": "po-1001",
            "approval_level": 2,
            "approver_id": "usr-04",
            "assigned_date": "2026-08-17T14:30:00",
            "status": "Pending",
            "comments": "Awaiting Finance Manager sign-off for PO-2026-001001"
        },
        {
            "id": "app-03",
            "transaction_type": "INDENT",
            "transaction_id": "ind-1002",
            "approval_level": 1,
            "approver_id": "usr-04",
            "assigned_date": "2026-08-17T11:00:00",
            "status": "Pending",
            "comments": "Awaiting Department Manager Stock Review for cabling"
        }
    ]

    db["approval_delegations"] = [
        {
            "id": "del-01",
            "delegator_id": "usr-04",
            "delegator_name": "Sarah Jenkins",
            "delegatee_id": "usr-02",
            "delegatee_name": "Jane Smith",
            "from_user": "usr-04",
            "to_user": "usr-02",
            "start_date": "2026-08-15",
            "end_date": "2026-08-31",
            "reason": "Annual Vacation Approval Delegation",
            "status": "Active",
            "is_active": True
        }
    ]

    db["approval_actions"] = [
        {
            "id": "act-01",
            "approval_id": "app-03-hist",
            "transaction_type": "INDENT",
            "transaction_id": "ind-1003",
            "approver_id": "usr-04",
            "approver_name": "Sarah Jenkins",
            "action": "Approve",
            "status": "Approved",
            "comments": "Approved IT hardware requisition for developer team setup.",
            "timestamp": "2026-08-15T10:30:00"
        },
        {
            "id": "act-02",
            "approval_id": "app-04-hist",
            "transaction_type": "INDENT",
            "transaction_id": "ind-1004",
            "approver_id": "usr-04",
            "approver_name": "Sarah Jenkins",
            "action": "Return",
            "status": "Returned for Correction",
            "comments": "Please specify preferred brand and technical specifications for cabling drums.",
            "timestamp": "2026-08-14T12:00:00"
        },
        {
            "id": "act-03",
            "approval_id": "app-05-hist",
            "transaction_type": "INDENT",
            "transaction_id": "ind-1005",
            "approver_id": "usr-04",
            "approver_name": "Sarah Jenkins",
            "action": "Reject",
            "status": "Rejected",
            "comments": "Exceeds annual department budget limits without senior management authorization.",
            "timestamp": "2026-08-12T16:15:00"
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
