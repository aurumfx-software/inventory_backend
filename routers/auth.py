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

    user = next((u for u in db.get("users", []) if u["email"].lower() == email), None)

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
