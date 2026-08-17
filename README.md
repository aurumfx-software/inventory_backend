# Enterprise Inventory & Procurement System - FastAPI Backend

100% Standalone **Python & FastAPI** backend service for Enterprise Inventory & Procurement Desktop Application.

## Technology Stack
- **Framework:** FastAPI
- **ASGI Server:** Uvicorn
- **Validation Schemas:** Pydantic
- **Auth:** PyJWT & Passlib
- **Data Persistence:** File-synced JSON Store (`inventory_store.json`)

## How to Run

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start FastAPI Development Server:**
   ```bash
   python run_server.py
   ```
   Or via Uvicorn directly:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

3. **Interactive API Documentation (Swagger UI):**
   Access openapi docs at: `http://127.0.0.1:8000/docs`
