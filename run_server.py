import sys
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    is_dev = os.getenv("ENVIRONMENT", "production").lower() in ["dev", "development"]
    print("===================================================")
    print(f" Starting Inventory & Procurement FastAPI Server...")
    print(f" Host: {host} | Port: {port}")
    print("===================================================")
    uvicorn.run("main:app", host=host, port=port, reload=is_dev)

