# Enterprise Inventory & Procurement System - FastAPI Backend

100% Standalone **Python & FastAPI** backend service for Enterprise Inventory & Procurement Desktop Application.

## Technology Stack
- **Framework:** FastAPI
- **ASGI Server:** Uvicorn
- **ORM & Driver:** SQLAlchemy & Psycopg2
- **Database Engine:** PostgreSQL
- **Validation Schemas:** Pydantic
- **Auth:** PyJWT & Passlib


## How to Run

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run PostgreSQL Database Migration:**
   ```bash
   python scripts/migrate_to_postgres.py
   ```

4. **Start FastAPI Development Server:**
   ```bash
   python run_server.py
   ```
   Or via Uvicorn directly:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

3. **Interactive API Documentation (Swagger UI):**
   Access openapi docs at: `http://127.0.0.1:8000/docs`
