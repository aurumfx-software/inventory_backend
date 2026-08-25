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
                current_ids = set()
                for idx, item in enumerate(records):
                    if isinstance(item, dict):
                        item_id = str(item.get("id", f"{table_name}-{idx+1}"))
                        payload_val = item
                    else:
                        item_id = str(item)
                        payload_val = {"id": str(item), "name": str(item)}

                    current_ids.add(item_id)
                    existing = session.query(model_cls).filter_by(id=item_id).first()
                    if not existing:
                        obj = model_cls(id=item_id, payload=payload_val)
                        session.add(obj)
                    else:
                        existing.payload = payload_val
                        from sqlalchemy.orm.attributes import flag_modified
                        flag_modified(existing, "payload")

                if current_ids:
                    session.query(model_cls).filter(~model_cls.id.in_(current_ids)).delete(synchronize_session=False)
                else:
                    session.query(model_cls).delete(synchronize_session=False)
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

def purge_all_sample_data():
    """Wipe out all sample records (items, suppliers, departments, warehouses, categories, brands, indents, POs, approvals, etc.) for a 100% fresh system."""
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
                print("[DB PURGE] All sample items, suppliers, departments, warehouses, and transactions permanently purged from PostgreSQL.")
            except Exception as e:
                session.rollback()
                print("[DB ERROR] Failed purging sample data:", e)
            finally:
                session.close()
    except Exception as err:
        print("[DB ERROR] Purge connect error:", err)

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

            # Force purge all sample items, suppliers, departments, warehouses, and transactions to ensure 100% fresh software
            purge_all_sample_data()

            # Always preserve default system login accounts
            if not db.get("users"):
                db["users"] = [
                    {"id": "usr-01", "name": "Sarah Jenkins", "email": "admin@company.com", "password": "password123", "role_id": "role-admin", "emp_code": "EMP-001", "department_id": "dept-01", "branch_id": "br-01", "is_active": True},
                    {"id": "usr-02", "name": "Rajesh Kumar", "email": "purchase@company.com", "password": "password123", "role_id": "role-purchase", "emp_code": "EMP-002", "department_id": "dept-02", "branch_id": "br-01", "is_active": True},
                    {"id": "usr-03", "name": "Michael Chang", "email": "store@company.com", "password": "password123", "role_id": "role-store", "emp_code": "EMP-003", "department_id": "dept-03", "branch_id": "br-01", "is_active": True},
                    {"id": "usr-04", "name": "Dr. Ananya Roy", "email": "deptmgr@company.com", "password": "password123", "role_id": "role-dept-mgr", "emp_code": "EMP-004", "department_id": "dept-01", "branch_id": "br-01", "is_active": True},
                    {"id": "usr-05", "name": "David Miller", "email": "requester@company.com", "password": "password123", "role_id": "role-requester", "emp_code": "EMP-005", "department_id": "dept-01", "branch_id": "br-01", "is_active": True},
                    {"id": "usr-06", "name": "Priya Sharma", "email": "finance@company.com", "password": "password123", "role_id": "role-finance", "emp_code": "EMP-006", "department_id": "dept-04", "branch_id": "br-01", "is_active": True},
                    {"id": "usr-07", "name": "Robert Wilson", "email": "auditor@company.com", "password": "password123", "role_id": "role-auditor", "emp_code": "EMP-007", "department_id": "dept-04", "branch_id": "br-01", "is_active": True}
                ]
                save_db()

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

    db["departments"] = []
    db["warehouses"] = []
    db["warehouse_locations"] = []
    db["item_categories"] = []
    db["brands"] = []

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

    db["items"] = []
    db["suppliers"] = []
    db["inventory_balances"] = []

    db["indents"] = []
    db["purchase_orders"] = []

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
