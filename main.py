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
    db_status = "Connected (PostgreSQL)" if check_db_connection() else "Disconnected (Falling back to local JSON store)"
    return {
        "success": True,
        "status": "UP",
        "database": db_status,
        "message": "Inventory & Procurement Python FastAPI Server Running",
        "engine": "FastAPI (Python 3)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
