import os
import re
from fastapi import APIRouter, HTTPException, Request, Header
from db.database_store import db, save_db
from schemas.schemas import LoginRequest, RegisterRequest, RoleSwitchRequest
import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/auth", tags=["Auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "inventory-procurement-secret-key-2026")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

from email_validator import validate_email, EmailNotValidError

DISPOSABLE_DUMMY_DOMAINS = {
    "tempmail.com", "mailinator.com", "10minutemail.com", "dispostable.com", 
    "trashmail.com", "getairmail.com", "guerrillamail.com", "maildrop.cc",
    "dummy.com", "test.com", "example.com", "fake.com", "dummy.in", "test.in",
    "fake.in", "testmail.com", "dummymail.com"
}

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

def validate_real_email(email: str):
    clean = (email or "").strip().lower()
    if not clean:
        raise HTTPException(
            status_code=400,
            detail="Email address is required."
        )
    try:
        valid_info = validate_email(clean, check_deliverability=False)
        normalized_email = valid_info.normalized
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Email Format: Please enter a valid email address (e.g. name@company.com or name@gmail.com)."
        )
    
    domain = normalized_email.split("@")[-1]
    if domain in DISPOSABLE_DUMMY_DOMAINS or "dummy" in domain or "fake" in domain or "tempmail" in domain:
        raise HTTPException(
            status_code=400,
            detail="Disposable/Fake Email Address Not Allowed: Please use a valid personal or work email address."
        )
    return normalized_email


@router.post("/login")
def login(req: LoginRequest):
    email = (req.email or "").lower().strip()
    password = req.password or ""

    if not email:
        raise HTTPException(status_code=400, detail="Email address is required.")

    if not password:
        raise HTTPException(status_code=400, detail="Password is required.")

    validate_real_email(email)

    DEFAULT_SYSTEM_USERS = [
        {"id": "usr-01", "name": "System Administrator", "email": "admin@company.com", "password": "admin123", "role_id": "role-admin", "emp_code": "EMP-001", "department_id": "dept-01", "is_active": True}
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
            "company_name": user.get("company_name", "Organization"),
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

@router.post("/register")
def register(req: RegisterRequest):
    email = (req.email or "").lower().strip()
    if not email:
        raise HTTPException(status_code=400, detail="Work Email is required.")
    
    validate_real_email(email)

    if not req.password:
        raise HTTPException(status_code=400, detail="Password is required.")

    # Check if user already exists
    existing = next((u for u in db.get("users", []) if u.get("email", "").lower() == email), None)
    if existing:
        raise HTTPException(status_code=400, detail="Email address is already registered. Please login with your password.")

    new_id = f"usr-{len(db.get('users', [])) + 101}"
    new_user = {
        "id": new_id,
        "name": req.full_name.strip(),
        "company_name": req.company_name.strip() if req.company_name else "Organization",
        "email": email,
        "phone": req.phone or "",
        "password": req.password,
        "role_id": req.role_id or "role-admin",
        "emp_code": f"EMP-{len(db.get('users', [])) + 101}",
        "department_id": "dept-01",
        "branch_id": "br-01",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }

    db["users"].append(new_user)
    save_db("users")

    # Add audit log for registration
    if "audit_logs" in db:
        db["audit_logs"].append({
            "id": f"aud-{len(db['audit_logs']) + 101}",
            "timestamp": datetime.now().isoformat(),
            "user_id": new_id,
            "user_name": req.full_name.strip(),
            "action": "USER_REGISTERED",
            "category": "Authentication",
            "module": "User Registration",
            "record_id": new_id,
            "ip_address": "127.0.0.1",
            "device_browser": "Web App Sign-up",
            "details": f"New user {req.full_name} registered account for company {req.company_name}.",
            "old_value": None,
            "new_value": {"email": email, "company": req.company_name},
            "reason": "Self-service Commercial Product Registration"
        })
        save_db("audit_logs")

    return {
        "success": True,
        "message": f"Account created successfully for {req.full_name}! You can now login.",
        "data": new_user
    }

@router.get("/profile")
def profile(request: Request, x_user_email: str = Header(None)):
    email = (x_user_email or request.headers.get("x-user-email") or "").strip().lower()
    user = next((u for u in db.get("users", []) if u.get("email", "").lower() == email), None)
    if not user and db.get("users"):
        user = db["users"][0]
    return {"success": True, "user": user}
