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
    "settings": {}
}



def save_db(target_table: str = None):
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
                    session.merge(model_cls(id=item_id, payload=payload_val))

                # Clean up deleted records
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
                else:
                    db[table_name] = []

            if not loaded_any:
                print("[POSTGRES DB INFO] PostgreSQL database tables are empty.")
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

    db["users"] = []

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
    db["stock_count_sessions"] = []

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
            "reason": "Quarterly Audit Compliance Check"
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
    Strict User & Tenant Data Isolation Helper:
    - Master Super Administrator (admin@company.com) sees all records across all users.
    - Individual users (e.g. Ashin, Ramu) see records created by themselves or under their company.
    """
    clean_email = str(user_email or "").strip().lower()
    clean_co = str(company_name or "").strip().lower()

    if clean_email in ["admin@company.com", "system administrator", "admin"]:
        return records

    if not clean_email and not clean_co:
        return records

    filtered = []
    for r in records:
        created_by = str(r.get("created_by", "") or r.get("created_by_email", "") or r.get("user_email", "")).strip().lower()
        record_co = str(r.get("company_name", "") or r.get("company", "")).strip().lower()
        is_sample = r.get("is_sample", False) or r.get("is_global", False)

        if is_sample or (clean_email and created_by == clean_email) or (clean_co and record_co and record_co == clean_co):
            filtered.append(r)
    return filtered

# Load database on import
load_db()
