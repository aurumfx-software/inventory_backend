import os
from fastapi import APIRouter, HTTPException
from db.database_store import db, save_db
from schemas.schemas import LoginRequest, RoleSwitchRequest
import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/auth", tags=["Auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "inventory-procurement-secret-key-2026")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


@router.post("/login")
def login(req: LoginRequest):
    email = (req.email or "").lower().strip()
    password = req.password or ""

    if not email:
        raise HTTPException(status_code=400, detail="Email address is required.")

    if not password:
        raise HTTPException(status_code=400, detail="Password is required.")

    DEFAULT_SYSTEM_USERS = [
        {"id": "usr-01", "name": "Sarah Jenkins", "email": "admin@company.com", "password": "password123", "role_id": "role-admin", "emp_code": "EMP-001", "department_id": "dept-01", "is_active": True},
        {"id": "usr-02", "name": "Rajesh Kumar", "email": "purchase@company.com", "password": "password123", "role_id": "role-purchase", "emp_code": "EMP-002", "department_id": "dept-02", "is_active": True},
        {"id": "usr-03", "name": "Michael Chang", "email": "store@company.com", "password": "password123", "role_id": "role-store", "emp_code": "EMP-003", "department_id": "dept-03", "is_active": True},
        {"id": "usr-04", "name": "Dr. Ananya Roy", "email": "deptmgr@company.com", "password": "password123", "role_id": "role-dept-mgr", "emp_code": "EMP-004", "department_id": "dept-01", "is_active": True},
        {"id": "usr-05", "name": "David Miller", "email": "requester@company.com", "password": "password123", "role_id": "role-requester", "emp_code": "EMP-005", "department_id": "dept-01", "is_active": True},
        {"id": "usr-06", "name": "Priya Sharma", "email": "finance@company.com", "password": "password123", "role_id": "role-finance", "emp_code": "EMP-006", "department_id": "dept-04", "is_active": True},
        {"id": "usr-07", "name": "Robert Wilson", "email": "auditor@company.com", "password": "password123", "role_id": "role-auditor", "emp_code": "EMP-007", "department_id": "dept-04", "is_active": True}
    ]

    user = next((u for u in db.get("users", []) if u.get("email", "").lower() == email), None)
    if not user:
        user = next((u for u in DEFAULT_SYSTEM_USERS if u["email"].lower() == email), None)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication Failed: Invalid email address. Access denied."
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=403,
            detail="Account Suspended: User account is inactive. Please contact Administrator."
        )

    expected_password = user.get("password", "password123")
    if password != expected_password:
        raise HTTPException(
            status_code=401,
            detail="Authentication Failed: Incorrect password. Access denied."
        )

    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "role_id": user["role_id"],
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    role = next((r for r in db.get("roles", []) if r["id"] == user["role_id"]), None)

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "emp_code": user["emp_code"],
            "role_id": user["role_id"],
            "role": role["name"] if role else "User",
            "department_id": user.get("department_id", "dept-01")
        }
    }

@router.post("/switch-role")
def switch_role(req: RoleSwitchRequest):
    role = next((r for r in db["roles"] if r["id"] == req.role_id), None)
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role_id")

    return {
        "success": True,
        "role_id": role["id"],
        "role_name": role["name"]
    }

@router.get("/profile")
def profile():
    return {"success": True, "user": db["users"][0]}
