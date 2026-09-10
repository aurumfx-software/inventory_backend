import sys
import os
import json

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from db.database_store import db, save_db

def import_server_db():
    print("\n=================================================================")
    print(" IMPORTING LOCAL DATABASE SNAPSHOT INTO SERVER POSTGRESQL DB")
    print("=================================================================\n")
    
    export_path = os.path.join(os.path.dirname(__file__), "full_database_export.json")
    
    if not os.path.exists(export_path):
        print(f"[ERROR] Snapshot file not found at: {export_path}")
        return
        
    with open(export_path, "r", encoding="utf-8") as f:
        imported_db = json.load(f)
        
    for k, v in imported_db.items():
        db[k] = v
        
    save_db()
    
    print("\n=================================================================")
    print(" [SUCCESS] ALL LOCAL DATA, TEST USERS, STOCKS, INDENTS & PAGE DATA")
    print(" HAVE BEEN SUCCESSFULLY IMPORTED & SAVED TO SERVER POSTGRESQL DB!")
    print("=================================================================\n")

if __name__ == "__main__":
    import_server_db()
