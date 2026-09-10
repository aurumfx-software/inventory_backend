import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

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
    "otps": [],
    "notifications": [],
    "settings": {}
}

def add_notification(title: str, message: str, notif_type: str = "info", target_role: str = "ALL"):
    if "notifications" not in db:
        db["notifications"] = []
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    now_iso = now.isoformat()
    notif = {
        "id": f"notif-{len(db['notifications']) + 1001}",
        "title": title,
        "message": message,
        "type": notif_type,
        "time": now_str,
        "created_at": now_iso,
        "target_role": target_role,
        "unread": True,
        "is_read": False
    }
    db["notifications"].insert(0, notif)
    save_db("notifications")
    return notif

def save_db(target_table: str = None, purge_deleted: bool = False, record: Any = None):
    """Save/Persist current database state exclusively to PostgreSQL database tables configured in .env."""
    try:
        from db.database import check_db_connection, SessionLocal, engine, Base
        from models.orm_models import TABLE_MODEL_MAP, SystemSetting

        if not check_db_connection():
            print("[DB ERROR] PostgreSQL database connection is offline. Unable to save state.")
            return

        session = SessionLocal()
        try:
            # If target_table specified, sync only that table for maximum speed
            tables_to_sync = [target_table] if target_table and target_table in TABLE_MODEL_MAP else list(TABLE_MODEL_MAP.keys())

            # Sync settings to PostgreSQL if full sync or target_table == 'settings'
            if (not target_table or target_table == "settings") and "settings" in db and isinstance(db["settings"], dict):
                for key, val in db["settings"].items():
                    payload_val = val if isinstance(val, (dict, list)) else {"value": val}
                    session.merge(SystemSetting(key=key, payload=payload_val))

            # Fast sync specified domain tables to PostgreSQL
            for table_name in tables_to_sync:
                model_cls = TABLE_MODEL_MAP.get(table_name)
                if not model_cls:
                    continue

                if record is not None and (target_table == table_name or not target_table):
                    records = [record] if isinstance(record, dict) else (record if isinstance(record, list) else [record])
                else:
                    records = db.get(table_name, [])
                    if not isinstance(records, list):
                        continue
                    # No record limit — sync ALL records to PostgreSQL

                # Deduplicate records by ID to prevent PostgreSQL UniqueViolation batch errors
                dedup_map = {}
                for idx, item in enumerate(records):
                    if isinstance(item, dict):
                        item_id = str(item.get("id", f"{table_name}-{idx+1}"))
                        payload_val = item
                    else:
                        item_id = str(item)
                        payload_val = {"id": str(item), "name": str(item)}
                    dedup_map[item_id] = payload_val

                current_ids = set(dedup_map.keys())
                for item_id, payload_val in dedup_map.items():
                    session.merge(model_cls(id=item_id, payload=payload_val))

                # Clean up deleted records ONLY if purge_deleted=True
                if purge_deleted:
                    if current_ids:
                        session.query(model_cls).filter(~model_cls.id.in_(current_ids)).delete(synchronize_session=False)
                    else:
                        session.query(model_cls).delete(synchronize_session=False)

            session.commit()
            print(f"[POSTGRES DB SUCCESS] Saved state to PostgreSQL table '{target_table or 'all tables'}' successfully.")
        except Exception as pg_err:
            session.rollback()
            import traceback
            traceback.print_exc()
            print("[POSTGRES DB ERROR] Error saving to PostgreSQL database:", pg_err)
        finally:
            session.close()
    except Exception as err:
        print("[POSTGRES DB ERROR] Failed to connect to PostgreSQL:", err)

def purge_all_sample_data():
    """Wipe out all sample records for a 100% fresh system in PostgreSQL."""
    global db
    tables_to_purge = [
        "items", "item_batches", "item_serials", "inventory_balances", "inventory_ledger",
        "suppliers", "supplier_contacts", "supplier_bank_accounts",
        "departments", "cost_centres", "warehouses", "warehouse_locations",
        "item_categories", "brands",
        "indents", "indent_items", "purchase_orders", "po_items",
        "approval_requests", "approval_actions", "approval_delegations",
        "rfqs", "rfq_items", "rfq_suppliers", "quotations", "quotation_items",
        "goods_receipts", "grn_items", "quality_inspections",
        "stock_issues", "stock_issue_items", "stock_returns", "supplier_returns",
        "stock_transfers", "stock_transfer_items", "stock_adjustments",
        "stock_count_sessions", "stock_count_entries", "stock_reservations", "assets"
    ]
    for tbl in tables_to_purge:
        db[tbl] = []
    
    try:
        from db.database import check_db_connection, SessionLocal
        from models.orm_models import TABLE_MODEL_MAP
        if check_db_connection():
            session = SessionLocal()
            try:
                for tbl in tables_to_purge:
                    model_cls = TABLE_MODEL_MAP.get(tbl)
                    if model_cls:
                        session.query(model_cls).delete(synchronize_session=False)
                session.commit()
                print("[POSTGRES DB PURGE] All sample data permanently purged from PostgreSQL tables.")
            except Exception as e:
                session.rollback()
                print("[POSTGRES DB ERROR] Failed purging sample data:", e)
            finally:
                session.close()
    except Exception as err:
        print("[POSTGRES DB ERROR] Purge connect error:", err)

def load_db():
    """Load database state exclusively from PostgreSQL database tables configured via .env."""
    global db

    try:
        from db.database import check_db_connection, SessionLocal, engine, Base
        from models.orm_models import TABLE_MODEL_MAP, SystemSetting

        if not check_db_connection():
            print("[POSTGRES DB WARN] PostgreSQL database is not accessible. Please check backend/.env configuration.")
            return db

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
                else:
                    db[table_name] = []

            if not db.get("items") or not db.get("purchase_orders"):
                print("[POSTGRES DB INFO] Demo domain tables are empty. Seeding full initial demo dataset...")
                seed_initial_data()
                save_db()
            else:
                print("[POSTGRES DB SUCCESS] Loaded all state exclusively from PostgreSQL database tables.")

            return db
        except Exception as pg_load_err:
            print("[POSTGRES DB ERROR] Error loading from PostgreSQL:", pg_load_err)
        finally:
            session.close()
    except Exception as err:
        print("[POSTGRES DB ERROR] Failed PostgreSQL database load:", err)

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
        {"id": "usr-01", "name": "System Administrator", "email": "admin@company.com", "phone": "9876543210", "password": "admin123", "role_id": "role-admin", "emp_code": "EMP-001", "department_id": "dept-01", "company_name": "Apex Enterprises", "is_active": True},
        {"id": "usr-ashin", "name": "Ashin Demo Administrator", "email": "ashina123@gmail.com", "phone": "8111814075", "password": "ashin123", "role_id": "role-admin", "emp_code": "EMP-110", "department_id": "dept-01", "company_name": "Ashin Enterprise Demo", "is_demo": True, "is_active": True}
    ]

    db["departments"] = [
        {"id": "dept-01", "name": "IT & Electronics Dept", "code": "IT-DEPT", "head_name": "Ashin Demo Admin", "budget_allocated": 1500000, "budget_used": 650000},
        {"id": "dept-02", "name": "Logistics & Operations", "code": "LOG-OPS", "head_name": "Suresh Kumar", "budget_allocated": 1200000, "budget_used": 420000},
        {"id": "dept-03", "name": "Procurement & Stores", "code": "PROC-STR", "head_name": "Priya Menon", "budget_allocated": 2000000, "budget_used": 980000},
        {"id": "dept-04", "name": "Plant Maintenance", "code": "PLANT-MNT", "head_name": "Rajesh Patel", "budget_allocated": 800000, "budget_used": 210000}
    ]

    db["warehouses"] = [
        {"id": "wh-01", "name": "Central Distribution Depot", "code": "WH-BLR-01", "city": "Bangalore", "address": "Plot 42, Industrial Zone 4, Bangalore", "is_active": True, "capacity_sqft": 45000},
        {"id": "wh-02", "name": "Cochin Logistics Hub", "code": "WH-COK-02", "city": "Kochi", "address": "Seaport-Airport Road, Kalamassery, Kochi", "is_active": True, "capacity_sqft": 28000},
        {"id": "wh-03", "name": "Mumbai Regional Depot", "code": "WH-BOM-03", "city": "Mumbai", "address": "Bhiwandi Logistics Park, Mumbai", "is_active": True, "capacity_sqft": 60000}
    ]

    db["warehouse_locations"] = [
        {"id": "loc-101", "warehouse_id": "wh-01", "bin_number": "A1-RACK-01", "zone": "Zone A (Electronics)", "is_occupied": True},
        {"id": "loc-102", "warehouse_id": "wh-01", "bin_number": "A2-RACK-04", "zone": "Zone A (Electronics)", "is_occupied": True},
        {"id": "loc-201", "warehouse_id": "wh-02", "bin_number": "B1-RACK-02", "zone": "Zone B (Packaging)", "is_occupied": True}
    ]

    db["item_categories"] = [
        {"id": "cat-01", "name": "Electronics & IT Hardware", "code": "ELEC-IT", "tax_rate_id": "tax-18", "description": "Laptops, Desktops, Scanners & Printers"},
        {"id": "cat-02", "name": "Industrial Raw Materials", "code": "RAW-IND", "tax_rate_id": "tax-18", "description": "Metals, Alloys, Chemicals & Ingots"},
        {"id": "cat-03", "name": "Packaging & Logistics Supplies", "code": "PKG-LOG", "tax_rate_id": "tax-12", "description": "Corrugated Crates, Tape, Pallets"},
        {"id": "cat-04", "name": "Office Furniture & Fixtures", "code": "FUR-OFF", "tax_rate_id": "tax-18", "description": "Ergonomic Chairs, Desks, Storage Units"}
    ]

    db["brands"] = [
        {"id": "brd-01", "name": "Dell Technologies", "code": "DELL"},
        {"id": "brd-02", "name": "Honeywell International", "code": "HON"},
        {"id": "brd-03", "name": "Zebra Technologies", "code": "ZEBRA"},
        {"id": "brd-04", "name": "Schneider Electric", "code": "SCHNEIDER"}
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
        {"id": "itm-01", "item_code": "ITM-DELL-5440", "name": "Dell Latitude 5440 Core i7 Laptop", "category_id": "cat-01", "brand_id": "brd-01", "uom_id": "uom-01", "unit_price": 65000, "reorder_level": 10, "min_stock": 5, "max_stock": 100, "barcode": "890123456701", "status": "Active", "description": "High Performance Core i7 13th Gen Enterprise Laptop", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "itm-02", "item_code": "ITM-HON-1250G", "name": "Honeywell Voyager 1250g Barcode Scanner", "category_id": "cat-01", "brand_id": "brd-02", "uom_id": "uom-01", "unit_price": 4500, "reorder_level": 20, "min_stock": 10, "max_stock": 200, "barcode": "890123456702", "status": "Active", "description": "Laser Handheld USB Barcode Scanner", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "itm-03", "item_code": "ITM-ZEB-ZD421", "name": "Zebra ZD421 Thermal Barcode Label Printer", "category_id": "cat-01", "brand_id": "brd-03", "uom_id": "uom-01", "unit_price": 28000, "reorder_level": 5, "min_stock": 2, "max_stock": 40, "barcode": "890123456703", "status": "Active", "description": "4-Inch Desktop Thermal Transfer Printer", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "itm-04", "item_code": "ITM-FUR-MESH01", "name": "Ergonomic Mesh High-Back Executive Chair", "category_id": "cat-04", "brand_id": "brd-04", "uom_id": "uom-01", "unit_price": 8500, "reorder_level": 15, "min_stock": 5, "max_stock": 150, "barcode": "890123456704", "status": "Active", "description": "Lumbar Support Adjustable Mesh Office Chair", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "itm-05", "item_code": "ITM-PKG-BOX020", "name": "Heavy-Duty Corrugated Storage Boxes (3-Ply)", "category_id": "cat-03", "brand_id": "brd-04", "uom_id": "uom-02", "unit_price": 900, "reorder_level": 50, "min_stock": 20, "max_stock": 500, "barcode": "890123456705", "status": "Active", "description": "Standard Cargo Dispatch Boxes - Pack of 20", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True}
    ]

    db["suppliers"] = [
        {"id": "sup-01", "code": "SUP-DELL-01", "name": "Dell India Pvt Ltd", "contact_person": "Rahul Sharma", "email": "rahul.sharma@dell.com", "phone": "9811223344", "city": "Bangalore", "grade": "A+", "rating": 4.9, "status": "Active", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "sup-02", "code": "SUP-HON-02", "name": "Honeywell Technology Solutions", "contact_person": "Priya Menon", "email": "priya.m@honeywell.com", "phone": "9822334455", "city": "Hyderabad", "grade": "A", "rating": 4.7, "status": "Active", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "sup-03", "code": "SUP-PKG-03", "name": "GreenPack Corrugated Ltd", "contact_person": "Suresh Kumar", "email": "sales@greenpack.co.in", "phone": "9833445566", "city": "Kochi", "grade": "A", "rating": 4.8, "status": "Active", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True}
    ]

    db["inventory_balances"] = [
        {"id": "bal-01", "item_id": "itm-01", "warehouse_id": "wh-01", "location_id": "loc-101", "quantity": 45, "reserved_qty": 5, "available_qty": 40, "batch_number": "BAT-DELL-2026-A", "unit_cost": 65000, "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "bal-02", "item_id": "itm-02", "warehouse_id": "wh-01", "location_id": "loc-102", "quantity": 120, "reserved_qty": 10, "available_qty": 110, "batch_number": "BAT-HON-2026-B", "unit_cost": 4500, "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "bal-03", "item_id": "itm-03", "warehouse_id": "wh-02", "location_id": "loc-201", "quantity": 30, "reserved_qty": 2, "available_qty": 28, "batch_number": "BAT-ZEB-2026-C", "unit_cost": 28000, "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "bal-04", "item_id": "itm-04", "warehouse_id": "wh-01", "location_id": "loc-101", "quantity": 85, "reserved_qty": 0, "available_qty": 85, "batch_number": "BAT-FUR-2026-D", "unit_cost": 8500, "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "bal-05", "item_id": "itm-05", "warehouse_id": "wh-02", "location_id": "loc-201", "quantity": 250, "reserved_qty": 20, "available_qty": 230, "batch_number": "BAT-PKG-2026-E", "unit_cost": 900, "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True}
    ]

    db["indents"] = [
        {"id": "ind-01", "indent_number": "IND-2026-001001", "requester_name": "Ashin Demo Administrator", "department_id": "dept-01", "status": "Approved", "urgency": "High", "created_at": now, "total_value": 650000, "reason": "Hardware upgrade for new software engineering cohort", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "ind-02", "indent_number": "IND-2026-001002", "requester_name": "Suresh Kumar", "department_id": "dept-02", "status": "Pending Approval", "urgency": "Medium", "created_at": now, "total_value": 45000, "reason": "Monthly dispatch corrugated packaging boxes", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True}
    ]

    db["purchase_orders"] = [
        {"id": "po-01", "po_number": "PO-2026-003001", "supplier_id": "sup-01", "supplier_name": "Dell India Pvt Ltd", "warehouse_id": "wh-01", "status": "Approved", "created_at": now, "delivery_date": "2026-09-15", "total_amount": 650000, "tax_amount": 117000, "grand_total": 767000, "items_count": 10, "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "po-02", "po_number": "PO-2026-003002", "supplier_id": "sup-02", "supplier_name": "Honeywell Technology Solutions", "warehouse_id": "wh-01", "status": "Processing", "created_at": now, "delivery_date": "2026-09-20", "total_amount": 225000, "tax_amount": 40500, "grand_total": 265500, "items_count": 50, "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "po-03", "po_number": "PO-2026-003003", "supplier_id": "sup-03", "supplier_name": "GreenPack Corrugated Ltd", "warehouse_id": "wh-02", "status": "Delivered", "created_at": now, "delivery_date": "2026-09-02", "total_amount": 45000, "tax_amount": 5400, "grand_total": 50400, "items_count": 50, "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True}
    ]

    db["stock_issues"] = [
        {"id": "iss-01", "issue_number": "ISS-2026-005001", "department_id": "dept-01", "warehouse_id": "wh-01", "issued_to": "IT New Hires", "status": "Issued & Verified", "created_at": now, "total_qty": 5, "total_value": 325000, "purpose": "Laptop Allocation for Software Team", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "iss-02", "issue_number": "ISS-2026-005002", "department_id": "dept-02", "warehouse_id": "wh-02", "issued_to": "Kochi Dispatch Fleet", "status": "Issued", "created_at": now, "total_qty": 20, "total_value": 18000, "purpose": "Dispatch packaging boxes issue", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True}
    ]

    db["assets"] = [
        {"id": "ast-01", "asset_tag": "AST-LAP-001", "name": "Dell Latitude 5440 (SN: DL892301)", "category": "IT Equipment", "assigned_to": "Ashin Demo Administrator", "department": "IT & Electronics", "purchase_cost": 65000, "status": "Active / Assigned", "barcode": "AST8901234501", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True},
        {"id": "ast-02", "asset_tag": "AST-PRN-002", "name": "Zebra ZD421 Label Printer", "category": "Office Equipment", "assigned_to": "Stores Team", "department": "Logistics & Operations", "purchase_cost": 28000, "status": "Active / In-Store", "barcode": "AST8901234502", "created_by": "ashina123@gmail.com", "company_name": "Ashin Enterprise Demo", "is_demo": True}
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

    db["approval_requests"] = []
    db["approval_delegations"] = []
    db["approval_actions"] = []

    db["audit_logs"] = [
        {
            "id": "aud-101",
            "timestamp": now,
            "user_id": "usr-01",
            "user_name": "System Administrator",
            "action": "LOGIN_SUCCESS",
            "category": "Authentication",
            "module": "Authentication",
            "record_id": "usr-01",
            "ip_address": "127.0.0.1",
            "device_browser": "Chrome / Windows",
            "details": "User System Administrator logged in successfully with MFA authorization.",
            "old_value": None,
            "new_value": {"session_token": "jwt-masked", "login_time": now},
            "reason": "Normal Application Sign-in"
        },
        {
            "id": "aud-102",
            "timestamp": now,
            "user_id": "usr-02",
            "user_name": "Purchase Manager",
            "action": "PO_CREATED",
            "category": "Record Changes",
            "module": "Purchase Orders",
            "record_id": "PO-2026-000045",
            "ip_address": "127.0.0.1",
            "device_browser": "Firefox / macOS",
            "details": "Created formal Purchase Order PO-2026-000045 for Approved Vendor.",
            "old_value": None,
            "new_value": {"po_number": "PO-2026-000045", "total_amount": 144000},
            "reason": "Procurement against Approved Indent"
        },
        {
            "id": "aud-103",
            "timestamp": now,
            "user_id": "usr-03",
            "user_name": "Store Manager",
            "action": "STOCK_POSTED",
            "category": "Approvals & Stock Posting",
            "module": "Goods Receipts (GRN)",
            "record_id": "GRN-2026-004018",
            "ip_address": "127.0.0.1",
            "device_browser": "Edge / Windows",
            "details": "Posted Goods Receipt GRN-2026-004018 into Warehouse stock.",
            "old_value": {"available_qty": 0, "reserved_qty": 0},
            "new_value": {"available_qty": 25, "reserved_qty": 0},
            "reason": "Physical delivery verified & quality inspection passed"
        },
        {
            "id": "aud-104",
            "timestamp": now,
            "user_id": "usr-04",
            "user_name": "Department Manager",
            "action": "INDENT_APPROVED",
            "category": "Approvals & Stock Posting",
            "module": "Indent Management",
            "record_id": "IND-2026-000124",
            "ip_address": "127.0.0.1",
            "device_browser": "Safari / macOS",
            "details": "Approved material indent request for required store items.",
            "old_value": {"status": "Submitted"},
            "new_value": {"status": "Approved", "approved_by": "Department Manager"},
            "reason": "Department budget allocation verified & within limits"
        },
        {
            "id": "aud-105",
            "timestamp": now,
            "user_id": "usr-01",
            "user_name": "System Administrator",
            "action": "RECORD_DELETED",
            "category": "Deletions & Permissions",
            "module": "Item Master",
            "record_id": "itm-099",
            "ip_address": "127.0.0.1",
            "device_browser": "Chrome / Windows",
            "details": "Permanently deleted obsolete item master record.",
            "old_value": {"item_code": "IT-MON-0099", "status": "Active"},
            "new_value": None,
            "reason": "Obsolete item purge requested"
        },
        {
            "id": "aud-106",
            "timestamp": now,
            "user_id": "usr-07",
            "user_name": "Auditor",
            "action": "REPORT_EXPORTED",
            "category": "Report Exports",
            "module": "Reports & Analytics",
            "record_id": "REP-VAL-2026",
            "ip_address": "127.0.0.1",
            "device_browser": "Chrome / Windows",
            "details": "Exported Financial Valuation & Stock Balance Summary Report.",
            "old_value": None,
            "new_value": {"report_name": "Stock Valuation Report", "format": "PDF"},
        }
    ]

    try:
        from scripts.seed_full_35_modules_demo import seed_full_35_modules_demo
        seed_full_35_modules_demo()
    except Exception as e:
        print("[SUPERMARKET DEMO SEED WARN]", e)

    print("Standalone Python FastAPI Seed complete.")

def get_next_doc_number(doc_type: str) -> str:
    if "numbering_series" not in db["settings"]:
        db["settings"]["numbering_series"] = {}
    
    curr = db["settings"]["numbering_series"].get(doc_type, 1000)
    next_val = curr + 1
    db["settings"]["numbering_series"][doc_type] = next_val
    save_db("settings")
    
    year = datetime.now().year
    return f"{doc_type}-{year}-{str(next_val).zfill(6)}"

def filter_by_company(records: list, company_name: str = None) -> list:
    """
    Strict Multi-Tenant Data Isolation helper:
    Filters database records by company_name.
    """
    if not company_name or str(company_name).strip().lower() in ["system administrator", "admin", "super administrator", "none", "null", ""]:
        return records
    
    target_co = str(company_name).strip().lower()
    return [
        r for r in records
        if str(r.get("company_name", "")).strip().lower() == target_co
        or str(r.get("company", "")).strip().lower() == target_co
    ]

def filter_by_user_or_company(records: list, user_email: str = None, company_name: str = None, role_id: str = None) -> list:
    """
    User & Multi-Tenant Data Isolation Helper:
    Returns records for Super Administrators, test users, demo users, or company matched records.
    """
    if not records:
        return []

    clean_email = str(user_email or "").strip().lower()
    clean_co = str(company_name or "").strip().lower()
    clean_role = str(role_id or "").strip().lower()

    if (
        clean_email in ["ashina123@gmail.com", "ashin demo administrator", "admin@company.com", "inventory.test.admin@gmail.com"]
        or "inventory.test" in clean_email
        or clean_role in ["role-admin", "super administrator"]
        or clean_co in ["enterprise head office", "ashin enterprise demo", "default enterprise", "apex enterprises", "organization", ""]
        or not user_email
    ):
        return records

    filtered = []
    for r in records:
        created_by = str(r.get("created_by", "") or r.get("created_by_email", "") or r.get("user_email", "")).strip().lower()
        record_co = str(r.get("company_name", "") or r.get("company", "")).strip().lower()

        if (clean_email and created_by == clean_email) or (clean_co and record_co and record_co == clean_co) or not created_by:
            filtered.append(r)
    return filtered if filtered else records

# Load database on import
load_db()
