import sys
import os
import json

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from db.database_store import load_db, db

def export_local_db():
    print("\n=================================================================")
    print(" EXPORTING EXACT LOCAL POSTGRESQL DATABASE TO JSON SNAPSHOT")
    print("=================================================================\n")
    
    load_db()
    
    export_path = os.path.join(os.path.dirname(__file__), "full_database_export.json")
    
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
        
    print(f"[SUCCESS] Exported all tables & 30-page local dataset to:")
    print(f" -> {export_path}")
    print("\nTotal table record summary:")
    for k, v in db.items():
        if isinstance(v, list) and len(v) > 0:
            print(f" - {k}: {len(v)} records")
        elif isinstance(v, dict) and len(v) > 0:
            print(f" - {k}: {len(v)} keys")
            
    print("\n=================================================================")

if __name__ == "__main__":
    export_local_db()
