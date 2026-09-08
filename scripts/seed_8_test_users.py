import sys
import os

# Ensure backend directory is in python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from db.database_store import load_db, save_db, db

def seed_test_users():
    print("[TEST USER SEED] Loading current database state from PostgreSQL...")
    load_db()

    # 1. Ensure Required Roles Exist
    required_roles = [
        {"id": "role-admin", "name": "Super Administrator", "description": "Full system access & workflow configuration"},
        {"id": "role-requester", "name": "Employee / Requester", "description": "Create material indents & track requests"},
        {"id": "role-dept-mgr", "name": "Department Manager", "description": "Approve department indents & view consumption budgets"},
        {"id": "role-store", "name": "Store Manager", "description": "Manage GRN, Stock Issues, Transfers, Returns & Audits"},
        {"id": "role-purchase", "name": "Purchase Manager", "description": "Manage RFQs, Supplier Quotes, POs & Supplier Ratings"},
        {"id": "role-finance", "name": "Finance User", "description": "Review PO values, tax verification & financial approvals"},
        {"id": "role-auditor", "name": "Auditor", "description": "Read-only access to audit logs, stock ledger & reports"},
        {"id": "role-director", "name": "Director / High-Level Approver", "description": "High-level/final approval authority for high value POs & indents"}
    ]

    existing_role_ids = {r.get("id") for r in db.get("roles", [])}
    for r in required_roles:
        if r["id"] not in existing_role_ids:
            db.setdefault("roles", []).append(r)
        else:
            # Update existing role name if needed
            for ex in db.get("roles", []):
                if ex.get("id") == r["id"]:
                    ex["name"] = r["name"]
                    ex["description"] = r["description"]

    # 2. Ensure Required Departments Exist
    required_departments = [
        {"id": "dept-it", "name": "IT", "code": "IT"},
        {"id": "dept-stores", "name": "Stores", "code": "STORES"},
        {"id": "dept-purchase", "name": "Purchase", "code": "PURCHASE"},
        {"id": "dept-finance", "name": "Finance", "code": "FINANCE"},
        {"id": "dept-audit", "name": "Audit", "code": "AUDIT"},
        {"id": "dept-mgmt", "name": "Management", "code": "MGMT"}
    ]

    existing_dept_ids = {d.get("id") for d in db.get("departments", [])}
    existing_dept_names = {d.get("name") for d in db.get("departments", [])}
    for d in required_departments:
        if d["id"] not in existing_dept_ids and d["name"] not in existing_dept_names:
            db.setdefault("departments", []).append(d)

    # 3. Define 8 Test Users
    test_users = [
        {
            "id": "usr-test-01",
            "name": "System Admin",
            "emp_code": "EMP001",
            "email": "inventory.test.admin@gmail.com",
            "phone": "9000000001",
            "password": "Test@123",
            "role_id": "role-admin",
            "role_name": "Super Administrator",
            "department_id": "dept-it",
            "department_name": "IT",
            "branch": "Head Office",
            "branch_id": "br-01",
            "approval_limit": "Unlimited",
            "status": "Active",
            "is_active": True,
            "company_name": "Enterprise Head Office"
        },
        {
            "id": "usr-test-02",
            "name": "Rahul Employee",
            "emp_code": "EMP002",
            "email": "inventory.test.employee@gmail.com",
            "phone": "9000000002",
            "password": "Test@123",
            "role_id": "role-requester",
            "role_name": "Employee / Requester",
            "department_id": "dept-it",
            "department_name": "IT",
            "branch": "Head Office",
            "branch_id": "br-01",
            "approval_limit": 0,
            "status": "Active",
            "is_active": True,
            "reporting_manager_id": "usr-test-03",
            "reporting_manager": "Arun Department Manager",
            "company_name": "Enterprise Head Office"
        },
        {
            "id": "usr-test-03",
            "name": "Arun Department Manager",
            "emp_code": "EMP003",
            "email": "inventory.test.manager@gmail.com",
            "phone": "9000000003",
            "password": "Test@123",
            "role_id": "role-dept-mgr",
            "role_name": "Department Manager",
            "department_id": "dept-it",
            "department_name": "IT",
            "branch": "Head Office",
            "branch_id": "br-01",
            "approval_limit": 100000,
            "status": "Active",
            "is_active": True,
            "reporting_manager_id": "usr-test-08",
            "reporting_manager": "Rajesh Director",
            "company_name": "Enterprise Head Office"
        },
        {
            "id": "usr-test-04",
            "name": "Suresh Store Manager",
            "emp_code": "EMP004",
            "email": "inventory.test.store@gmail.com",
            "phone": "9000000004",
            "password": "Test@123",
            "role_id": "role-store",
            "role_name": "Store Manager",
            "department_id": "dept-stores",
            "department_name": "Stores",
            "branch": "Head Office",
            "branch_id": "br-01",
            "approval_limit": 200000,
            "status": "Active",
            "is_active": True,
            "reporting_manager_id": "usr-test-08",
            "reporting_manager": "Rajesh Director",
            "company_name": "Enterprise Head Office"
        },
        {
            "id": "usr-test-05",
            "name": "Vishnu Purchase Manager",
            "emp_code": "EMP005",
            "email": "inventory.test.purchase@gmail.com",
            "phone": "9000000005",
            "password": "Test@123",
            "role_id": "role-purchase",
            "role_name": "Purchase Manager",
            "department_id": "dept-purchase",
            "department_name": "Purchase",
            "branch": "Head Office",
            "branch_id": "br-01",
            "approval_limit": 500000,
            "status": "Active",
            "is_active": True,
            "reporting_manager_id": "usr-test-08",
            "reporting_manager": "Rajesh Director",
            "company_name": "Enterprise Head Office"
        },
        {
            "id": "usr-test-06",
            "name": "Anjali Finance",
            "emp_code": "EMP006",
            "email": "inventory.test.finance@gmail.com",
            "phone": "9000000006",
            "password": "Test@123",
            "role_id": "role-finance",
            "role_name": "Finance User",
            "department_id": "dept-finance",
            "department_name": "Finance",
            "branch": "Head Office",
            "branch_id": "br-01",
            "approval_limit": 500000,
            "status": "Active",
            "is_active": True,
            "reporting_manager_id": "usr-test-08",
            "reporting_manager": "Rajesh Director",
            "company_name": "Enterprise Head Office"
        },
        {
            "id": "usr-test-07",
            "name": "Audit User",
            "emp_code": "EMP007",
            "email": "inventory.test.auditor@gmail.com",
            "phone": "9000000007",
            "password": "Test@123",
            "role_id": "role-auditor",
            "role_name": "Auditor",
            "department_id": "dept-audit",
            "department_name": "Audit",
            "branch": "Head Office",
            "branch_id": "br-01",
            "approval_limit": 0,
            "status": "Active",
            "is_active": True,
            "reporting_manager_id": "usr-test-08",
            "reporting_manager": "Rajesh Director",
            "company_name": "Enterprise Head Office"
        },
        {
            "id": "usr-test-08",
            "name": "Rajesh Director",
            "emp_code": "EMP008",
            "email": "inventory.test.director@gmail.com",
            "phone": "9000000008",
            "password": "Test@123",
            "role_id": "role-director",
            "role_name": "Director / High-Level Approver",
            "department_id": "dept-mgmt",
            "department_name": "Management",
            "branch": "Head Office",
            "branch_id": "br-01",
            "approval_limit": 1000000,
            "status": "Active",
            "is_active": True,
            "company_name": "Enterprise Head Office"
        }
    ]

    # 4. Upsert users in db["users"] safely without duplicates
    existing_users = db.get("users", [])
    user_map = {u.get("email", "").lower().strip(): u for u in existing_users}
    code_map = {u.get("emp_code", "").strip(): u for u in existing_users}

    seeded_count = 0
    for u in test_users:
        u_email = u["email"].lower().strip()
        u_code = u["emp_code"].strip()

        target = user_map.get(u_email) or code_map.get(u_code)
        if target:
            target.update(u)
            print(f" [UPDATED] Existing user: {u['name']} ({u['email']}) - Code: {u['emp_code']}")
        else:
            existing_users.append(u)
            print(f" [CREATED] New user: {u['name']} ({u['email']}) - Code: {u['emp_code']}")
        seeded_count += 1

    db["users"] = existing_users

    # Save roles, departments, and users state to PostgreSQL DB via .env configuration
    save_db("roles")
    save_db("departments")
    save_db("users")

    print(f"\n[SUCCESS] Successfully seeded and verified {seeded_count} test users in PostgreSQL database!\n")

if __name__ == "__main__":
    seed_test_users()
