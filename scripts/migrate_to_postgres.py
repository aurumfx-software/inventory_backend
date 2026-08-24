import os
import sys
import json
from datetime import datetime

from dotenv import load_dotenv

# Add backend parent directory to sys.path and load environment variables
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

load_dotenv(os.path.join(backend_dir, ".env"))

from db.database import engine, Base, SessionLocal, check_db_connection
from models.orm_models import TABLE_MODEL_MAP, SystemSetting


def run_migration():
    print("=" * 60)
    print("PostgreSQL Database Migration Script")
    print("=" * 60)

    # 1. Check connection
    print("Checking PostgreSQL connection...")
    if not check_db_connection():
        print("[ERROR] Could not connect to PostgreSQL. Please check PostgreSQL server status and backend/.env credentials.")
        return False

    print("[SUCCESS] PostgreSQL connection verified!")

    # 2. Create tables
    print("Creating PostgreSQL database tables...")
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] Database tables created successfully.")

    # 3. Seed data directly from database_store seed definition
    from db.database_store import seed_initial_data, db as memory_db
    db_json_path = os.path.join(backend_dir, "db", "inventory_store.json")

    if os.path.exists(db_json_path):
        print(f"Loading seed data from {db_json_path}...")
        with open(db_json_path, "r", encoding="utf-8") as f:
            data_store = json.load(f)
    else:
        print("Initializing seed data into PostgreSQL directly...")
        seed_initial_data()
        data_store = memory_db


    session = SessionLocal()
    try:
        migrated_counts = {}

        # 4. Migrate system settings
        if "settings" in data_store and isinstance(data_store["settings"], dict):
            settings_dict = data_store["settings"]
            for key, val in settings_dict.items():
                setting_obj = session.query(SystemSetting).filter_by(key=key).first()
                if not setting_obj:
                    setting_obj = SystemSetting(key=key, payload=val if isinstance(val, (dict, list)) else {"value": val})
                    session.add(setting_obj)
                else:
                    setting_obj.payload = val if isinstance(val, (dict, list)) else {"value": val}
            migrated_counts["settings"] = len(settings_dict)

        # 5. Migrate all tables mapped in TABLE_MODEL_MAP
        for table_name, model_cls in TABLE_MODEL_MAP.items():
            records = data_store.get(table_name, [])
            if not isinstance(records, list):
                continue

            count = 0
            for idx, item in enumerate(records):
                if isinstance(item, dict):
                    item_id = str(item.get("id", f"{table_name}-{idx+1}"))
                    payload_val = item
                else:
                    item_id = str(item)
                    payload_val = {"id": str(item), "name": str(item)}

                existing = session.query(model_cls).filter_by(id=item_id).first()
                if not existing:
                    obj = model_cls(id=item_id, payload=payload_val)
                    session.add(obj)
                    count += 1
                else:
                    existing.payload = payload_val
                    count += 1

            migrated_counts[table_name] = count

        session.commit()
        print("[SUCCESS] Data Migration completed successfully!")
        print("\nSummary of records migrated to PostgreSQL:")
        for tbl, cnt in migrated_counts.items():
            print(f"  - {tbl}: {cnt} records")

        print("=" * 60)
        return True
    except Exception as err:
        session.rollback()
        import traceback
        traceback.print_exc()
        print(f"[ERROR] Migration failed: {err}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    run_migration()
