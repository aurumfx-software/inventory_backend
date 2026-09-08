import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database_store import load_db

# Load environment variables
load_dotenv(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        ".env"
    )
)

from routers.auth import router as auth_router
from routers.masters import router as masters_router
from routers.indents import router as indents_router
from routers.approvals import router as approvals_router
from routers.procurement import router as procurement_router
from routers.inventory_ops import router as inventory_ops_router
from routers.reports import router as reports_router
from routers.settings_audit import router as settings_audit_router
from routers.dashboard import router as dashboard_router


# FastAPI is exposed externally through Nginx at /api
root_path = os.getenv("ROOT_PATH", "")

app = FastAPI(
    title="Inventory & Procurement System API",
    description="Enterprise Python & FastAPI Backend for Inventory & Procurement Desktop Application",
    version="1.0.0",
    root_path=root_path
)

@app.on_event("startup")
def startup_event():
    print("[SERVER STARTUP] Automatically initializing PostgreSQL tables and sync state...")
    load_db()


cors_origins_raw = os.getenv("CORS_ORIGINS", "*")

cors_origins = (
    [origin.strip() for origin in cors_origins_raw.split(",")]
    if cors_origins_raw != "*"
    else ["*"]
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_router)
app.include_router(masters_router)
app.include_router(indents_router)
app.include_router(approvals_router)
app.include_router(procurement_router)
app.include_router(inventory_ops_router)
app.include_router(reports_router)
app.include_router(settings_audit_router)
app.include_router(dashboard_router)

# Shorthand Top-Level API Endpoints for Direct Data Access
@app.get("/api/seed-demo")
def trigger_seed_demo():
    from db.database_store import seed_initial_data, save_db, load_db
    seed_initial_data()
    save_db()
    load_db()
    return {"success": True, "message": "Demo dataset populated and loaded into memory successfully!"}

@app.get("/api/items")
def get_shorthand_items():
    from db.database_store import db, seed_initial_data, save_db, load_db
    items = db.get("items", [])
    if not items:
        seed_initial_data()
        save_db()
        load_db()
        items = db.get("items", [])
    return {"success": True, "data": items, "count": len(items)}

@app.get("/api/indents")
def get_shorthand_indents():
    from db.database_store import db, seed_initial_data, save_db, load_db
    indents = db.get("indents", [])
    if not indents:
        seed_initial_data()
        save_db()
        load_db()
        indents = db.get("indents", [])
    return {"success": True, "data": indents, "count": len(indents)}

@app.get("/api/purchase-orders")
def get_shorthand_pos():
    from db.database_store import db, seed_initial_data, save_db, load_db
    pos = db.get("purchase_orders", [])
    if not pos:
        seed_initial_data()
        save_db()
        load_db()
        pos = db.get("purchase_orders", [])
    return {"success": True, "data": pos, "count": len(pos)}

@app.get("/api/goods-receipts")
def get_shorthand_grns():
    from db.database_store import db, seed_initial_data, save_db, load_db
    grns = db.get("goods_receipts", [])
    if not grns:
        seed_initial_data()
        save_db()
        load_db()
        grns = db.get("goods_receipts", [])
    return {"success": True, "data": grns, "count": len(grns)}

@app.get("/api/suppliers")
def get_shorthand_suppliers():
    from db.database_store import db, seed_initial_data, save_db, load_db
    suppliers = db.get("suppliers", [])
    if not suppliers:
        seed_initial_data()
        save_db()
        load_db()
        suppliers = db.get("suppliers", [])
    return {"success": True, "data": suppliers, "count": len(suppliers)}

@app.get("/api/warehouses")
def get_shorthand_warehouses():
    from db.database_store import db, seed_initial_data, save_db, load_db
    warehouses = db.get("warehouses", [])
    if not warehouses:
        seed_initial_data()
        save_db()
        load_db()
        warehouses = db.get("warehouses", [])
    return {"success": True, "data": warehouses, "count": len(warehouses)}

@app.get("/api/stock-issues")
def get_shorthand_stock_issues():
    from db.database_store import db, seed_initial_data, save_db, load_db
    issues = db.get("stock_issues", [])
    if not issues:
        seed_initial_data()
        save_db()
        load_db()
        issues = db.get("stock_issues", [])
    return {"success": True, "data": issues, "count": len(issues)}

@app.get("/api/inventory-balances")
def get_shorthand_balances():
    from db.database_store import db, seed_initial_data, save_db, load_db
    balances = db.get("inventory_balances", [])
    if not balances:
        seed_initial_data()
        save_db()
        load_db()
        balances = db.get("inventory_balances", [])
    return {"success": True, "data": balances, "count": len(balances)}

# Root Endpoint
@app.get("/")
def root():
    return {
        "success": True,
        "message": "Inventory & Procurement API Backend is running.",
        "docs": "/api/docs",
        "health": "/api/health"
    }

# Fallback endpoint for /openapi.json
@app.get("/openapi.json", include_in_schema=False)
def get_openapi_schema_fallback():
    return app.openapi()

# Healthcheck Endpoint
@app.get("/api/health")
def healthcheck():
    from db.database import check_db_connection
    db_status = "Connected (PostgreSQL)" if check_db_connection() else "Disconnected (PostgreSQL Connection Failed)"
    return {
        "success": True,
        "status": "UP",
        "database": db_status,
        "message": "Inventory & Procurement Python FastAPI Server Running",
        "engine": "FastAPI (Python 3)"
    }


if __name__ == "__main__":
    import uvicorn
    is_dev = os.getenv("ENVIRONMENT", "production").lower() in ["dev", "development"]
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=is_dev)
