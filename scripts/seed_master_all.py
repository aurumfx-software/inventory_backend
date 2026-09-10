import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scripts.seed_8_test_users import seed_test_users
from scripts.setup_full_test_environment import setup_full_test_environment
from scripts.seed_full_35_modules_demo import seed_full_35_modules_demo

def seed_everything():
    print("\n=================================================================")
    print(" SEEDING COMPLETE SYSTEM DATA (TEST USERS + STOCKS + INDENTS + POs)")
    print(" Target DB: PostgreSQL configured in .env")
    print("=================================================================\n")
    
    print("[STEP 1/3] Seeding 8 Test Users and System Roles into PostgreSQL...")
    seed_test_users()
    
    print("\n[STEP 2/3] Setting up Enterprise Catalog, Items, Suppliers & Material Indents...")
    setup_full_test_environment()
    
    print("\n[STEP 3/3] Populating Inventory Balances, Stock Operations & Demo Modules...")
    seed_full_35_modules_demo()
    
    print("\n=================================================================")
    print(" [SUCCESS] ALL TEST DATA, STOCKS, INDENTS & USERS SEEDED TO POSTGRESQL!")
    print("=================================================================\n")

if __name__ == "__main__":
    seed_everything()
