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
    
    # Load all imported data into the in-memory db
    for k, v in imported_db.items():
        db[k] = v
    
    # Print summary of what we're importing
    print("Data to import:")
    for k, v in db.items():
        if isinstance(v, list) and len(v) > 0:
            print(f"  - {k}: {len(v)} records")
        elif isinstance(v, dict) and len(v) > 0:
            print(f"  - {k}: {len(v)} keys")
    
    # Save ALL records to PostgreSQL, table by table, with purge_deleted=True
    # This ensures complete sync and removes any stale server records
    print("\nSyncing to PostgreSQL (full sync with purge_deleted=True)...")
    
    # First save settings
    save_db("settings", purge_deleted=True)
    print("  [OK] settings")
    
    # Then save each table individually for reliable complete sync
    from models.orm_models import TABLE_MODEL_MAP
    for table_name in TABLE_MODEL_MAP.keys():
        if table_name in db:
            save_db(table_name, purge_deleted=True)
            count = len(db[table_name]) if isinstance(db[table_name], list) else 0
            print(f"  [OK] {table_name}: {count} records synced")
    
    print("\n=================================================================")
    print(" [SUCCESS] ALL LOCAL DATA, TEST USERS, STOCKS, INDENTS & PAGE DATA")
    print(" HAVE BEEN SUCCESSFULLY IMPORTED & SAVED TO SERVER POSTGRESQL DB!")
    print("=================================================================\n")

if __name__ == "__main__":
    import_server_db()
