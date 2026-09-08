import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database_store import db, save_db

def seed_full_35_modules_demo():
    print("=================================================================")
    print(" Populating Full Supermarket Demo Data Across All 35 Modules")
    print(" Target User: ashina123@gmail.com (Ashin Enterprise Demo)")
    print(" Persistence: PostgreSQL Database configured in .env")
    print("=================================================================")

    DEMO_USER = "ashina123@gmail.com"
    DEMO_COMPANY = "Ashin Enterprise Demo"
    IS_DEMO = True
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d")

    # -------------------------------------------------------------------------
    # 1. System Settings (sec-32)
    # -------------------------------------------------------------------------
    db["settings"] = {
        "company_name": "Ashin Supermarket & Retail Enterprise",
        "company_logo": "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=100&auto=format&fit=crop&q=60",
        "address": "Kochi Supermarket Hub, Seaport-Airport Road, Kochi, Kerala, India",
        "tax_number": "32AAAAA1234A1Z9",
        "contact_email": "ashina123@gmail.com",
        "contact_phone": "8111814075",
        "financial_year": "2026-2027",
        "allow_negative_stock": False,
        "valuation_method": "FIFO",
        "default_warehouse_id": "wh-01",
        "expiry_warning_days": 30,
        "decimal_precision_qty": 2,
        "decimal_precision_currency": 2,
        "numbering_series": {
            "IND": 1010,
            "RFQ": 2010,
            "PO": 3010,
            "GRN": 4010,
            "ISS": 5010,
            "TRN": 6010,
            "ADJ": 7010,
            "QI": 8010
        }
    }

    # -------------------------------------------------------------------------
    # 2. User Management (sec-10)
    # -------------------------------------------------------------------------
    demo_users = [
        {"id": "usr-ashin", "name": "Ashin Demo Administrator", "email": DEMO_USER, "phone": "8111814075", "password": "ashin123", "role_id": "role-admin", "role_name": "Super Administrator", "emp_code": "EMP-101", "department_name": "Store Admin & Operations", "branch": "Central Supermarket - Kochi", "reporting_manager": "Board of Directors", "approval_limit": 5000000, "is_active": True, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "usr-sm-suresh", "name": "Suresh Kumar", "email": "suresh.store@supermarket.com", "phone": "9845011111", "password": "password123", "role_id": "role-store", "role_name": "Store Manager", "emp_code": "EMP-102", "department_name": "Warehouse & Inventory", "branch": "Central Supermarket - Kochi", "reporting_manager": "Ashin Demo Administrator", "approval_limit": 500000, "is_active": True, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "usr-sm-priya", "name": "Priya Menon", "email": "priya.purchase@supermarket.com", "phone": "9845022222", "password": "password123", "role_id": "role-purchase", "role_name": "Purchase Manager", "emp_code": "EMP-103", "department_name": "Procurement & Sourcing", "branch": "Central Supermarket - Kochi", "reporting_manager": "Ashin Demo Administrator", "approval_limit": 1000000, "is_active": True, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "usr-sm-rajesh", "name": "Rajesh Patel", "email": "rajesh.dept@supermarket.com", "phone": "9845033333", "password": "password123", "role_id": "role-dept-mgr", "role_name": "Department Manager", "emp_code": "EMP-104", "department_name": "Fresh Foods & Dairy", "branch": "Central Supermarket - Kochi", "reporting_manager": "Ashin Demo Administrator", "approval_limit": 250000, "is_active": True, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "usr-sm-vikram", "name": "Vikram Verma", "email": "vikram.finance@supermarket.com", "phone": "9845044444", "password": "password123", "role_id": "role-finance", "role_name": "Finance User", "emp_code": "EMP-105", "department_name": "Finance & Accounts", "branch": "Central Supermarket - Kochi", "reporting_manager": "Ashin Demo Administrator", "approval_limit": 2000000, "is_active": True, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["users"] = [u for u in db.get("users", []) if u.get("created_by") != DEMO_USER and u.get("id") != "usr-ashin"]
    db["users"].extend(demo_users)

    # -------------------------------------------------------------------------
    # 3. Department Master (sec-8)
    # -------------------------------------------------------------------------
    demo_depts = [
        {"id": "dept-sm-01", "name": "Fresh Foods & Dairy Dept", "code": "DEPT-FRESH", "head_name": "Rajesh Patel", "budget_allocated": 500000, "budget_used": 180000, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "dept-sm-02", "name": "Packaged Grocery & Beverages", "code": "DEPT-GROCery", "head_name": "Priya Menon", "budget_allocated": 800000, "budget_used": 340000, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "dept-sm-03", "name": "Personal Care & Household Cleaning", "code": "DEPT-CARE", "head_name": "Suresh Kumar", "budget_allocated": 400000, "budget_used": 150000, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "dept-sm-04", "name": "Store Operations & Maintenance", "code": "DEPT-OPS", "head_name": "Ashin Demo Administrator", "budget_allocated": 600000, "budget_used": 210000, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["departments"] = [d for d in db.get("departments", []) if d.get("created_by") != DEMO_USER]
    db["departments"].extend(demo_depts)

    # -------------------------------------------------------------------------
    # 4. Warehouse & Locations (sec-9)
    # -------------------------------------------------------------------------
    demo_whs = [
        {"id": "wh-01", "name": "Kochi Central Supermarket Depot", "code": "WH-COK-01", "city": "Kochi", "address": "Seaport-Airport Road, Kalamassery, Kochi", "is_active": True, "capacity_sqft": 35000, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "wh-02", "name": "Kochi Cold Chain & Dairy Hub", "code": "WH-COK-COLD", "city": "Kochi", "address": "Industrial Zone, Edapally, Kochi", "is_active": True, "capacity_sqft": 15000, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "wh-03", "name": "Bangalore Regional Distribution Depot", "code": "WH-BLR-03", "city": "Bangalore", "address": "Whitefield Logistics Park, Bangalore", "is_active": True, "capacity_sqft": 50000, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["warehouses"] = [w for w in db.get("warehouses", []) if w.get("created_by") != DEMO_USER]
    db["warehouses"].extend(demo_whs)

    demo_locs = [
        {"id": "loc-101", "warehouse_id": "wh-01", "bin_number": "A1-RACK-01", "zone": "Zone A (Dry Grocery Racks)", "is_occupied": True, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "loc-102", "warehouse_id": "wh-01", "bin_number": "A2-RACK-04", "zone": "Zone A (Personal Care Racks)", "is_occupied": True, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "loc-201", "warehouse_id": "wh-02", "bin_number": "C1-COLD-CHILLER", "zone": "Zone C (Cold Chain & Fresh Dairy)", "is_occupied": True, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["warehouse_locations"] = [l for l in db.get("warehouse_locations", []) if l.get("created_by") != DEMO_USER]
    db["warehouse_locations"].extend(demo_locs)

    # -------------------------------------------------------------------------
    # 5. Categories & Brands
    # -------------------------------------------------------------------------
    sm_categories = [
        {"id": "cat-sm-01", "name": "Dairy, Bakery & Fresh Produce", "code": "FRESH-DAIRY", "tax_rate_id": "tax-5", "description": "Fresh Milk, Butter, Cheese, Bread & Farm Vegetables", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-02", "name": "Packaged Foods & Snacks", "code": "SNACK-PKG", "tax_rate_id": "tax-12", "description": "Biscuits, Chocolates, Chips & Ready-to-Eat Snacks", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-03", "name": "Beverages & Cold Drinks", "code": "BEV-DRINK", "tax_rate_id": "tax-18", "description": "Soft Drinks, Fruit Juices, Energy Drinks & Teas", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-04", "name": "Staples, Grains & Spices", "code": "STAPLE-GRN", "tax_rate_id": "tax-5", "description": "Atta, Rice, Pulses, Cooking Oils & Masalas", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-05", "name": "Personal Care & Hygiene", "code": "CARE-HYG", "tax_rate_id": "tax-18", "description": "Soaps, Shampoos, Toothpastes & Cosmetics", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-06", "name": "Household & Cleaning Supplies", "code": "CLEAN-HOU", "tax_rate_id": "tax-18", "description": "Detergents, Surface Cleaners & Dishwash Gels", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-07", "name": "Frozen Foods & Ice Creams", "code": "FRZN-ICE", "tax_rate_id": "tax-18", "description": "Frozen Fries, Ready Meals & Ice Cream Tubs", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["item_categories"] = [c for c in db.get("item_categories", []) if c.get("created_by") != DEMO_USER]
    db["item_categories"].extend(sm_categories)

    sm_brands = [
        {"id": "brd-sm-01", "name": "Amul (GCMMF)", "code": "AMUL", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "brd-sm-02", "name": "Britannia Industries", "code": "BRITAN", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "brd-sm-03", "name": "Nestlé India", "code": "NESTLE", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "brd-sm-04", "name": "Hindustan Unilever (HUL)", "code": "HUL", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "brd-sm-05", "name": "ITC Foods (Aashirvaad)", "code": "ITC", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "brd-sm-06", "name": "Parle Products", "code": "PARLE", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "brd-sm-07", "name": "Fortune Oils (Adani Wilmar)", "code": "FORTUNE", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "brd-sm-08", "name": "Coca-Cola & PepsiCo", "code": "BEV-CORP", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "brd-sm-09", "name": "Dabur & Real Juices", "code": "DABUR", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "brd-sm-10", "name": "McCain & MTR Foods", "code": "FROZEN-MTR", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["brands"] = [b for b in db.get("brands", []) if b.get("created_by") != DEMO_USER]
    db["brands"].extend(sm_brands)

    # -------------------------------------------------------------------------
    # 6. Supplier Directory (sec-7)
    # -------------------------------------------------------------------------
    sm_suppliers = [
        {"id": "sup-sm-01", "code": "SUP-AMUL-01", "name": "GCMMF Amul Milk & Dairy Wholesale", "contact_person": "Vikram Patel", "email": "supply@amul.coop", "phone": "9825012345", "city": "Anand / Kochi", "grade": "A+", "rating": 4.9, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "sup-sm-02", "code": "SUP-NESTLE-02", "name": "Nestlé India FMCG Distributors", "contact_person": "Meera Sen", "email": "orders@in.nestle.com", "phone": "9810098765", "city": "Bangalore", "grade": "A+", "rating": 4.8, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "sup-sm-03", "code": "SUP-HUL-03", "name": "Hindustan Unilever Wholesale Depot", "contact_person": "Rajesh Gupta", "email": "depot.hul@unilever.com", "phone": "9845011223", "city": "Kochi", "grade": "A+", "rating": 4.9, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "sup-sm-04", "code": "SUP-BRIT-04", "name": "Britannia Bakery Products Direct", "contact_person": "Anil Nair", "email": "sales@britindia.com", "phone": "9895033445", "city": "Kochi", "grade": "A", "rating": 4.7, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "sup-sm-05", "code": "SUP-ITC-05", "name": "ITC Agri & Staples Wholesale", "contact_person": "Karan Singhania", "email": "fmcg@itc.in", "phone": "9830055667", "city": "Mumbai", "grade": "A+", "rating": 4.9, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "sup-sm-06", "code": "SUP-BEV-06", "name": "United Beverage Bottlers (Coke & Pepsi)", "contact_person": "Deepak Roy", "email": "orders@beveragebottlers.in", "phone": "9871144556", "city": "Bangalore", "grade": "A", "rating": 4.6, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["suppliers"] = [s for s in db.get("suppliers", []) if s.get("created_by") != DEMO_USER]
    db["suppliers"].extend(sm_suppliers)

    # -------------------------------------------------------------------------
    # 7. 50 Supermarket Items (sec-6 & sec-20) - Total Stock Value = ₹18,000
    # -------------------------------------------------------------------------
    products_raw = [
        # Dairy & Bakery (cat-sm-01)
        ("SM-001", "Amul Taaza Toned Fresh Milk 1L Pouch", "cat-sm-01", "brd-sm-01", "uom-05", 54, 10, 5, 100, "890126201001", 6, 5, True), # Low stock & Expiring!
        ("SM-002", "Amul Pasteurised Salted Butter 500g Pack", "cat-sm-01", "brd-sm-01", "uom-01", 120, 10, 3, 50, "890126201002", 3, 12, True), # Low stock & Expiring!
        ("SM-003", "Amul Fresh Malai Paneer 200g Pouch", "cat-sm-01", "brd-sm-01", "uom-01", 90, 8, 2, 40, "890126201003", 4, 6, True), # Low stock & Expiring!
        ("SM-004", "Mother Dairy Fresh Dahi 400g Cup", "cat-sm-01", "brd-sm-01", "uom-01", 45, 10, 3, 60, "890126201004", 6, 5, True), # Low stock & Expiring!
        ("SM-005", "Britannia 100% Whole Wheat Bread 400g", "cat-sm-01", "brd-sm-02", "uom-01", 45, 12, 4, 80, "890126201005", 8, 3, True), # Low stock & Expiring!
        ("SM-006", "Nestlé Everyday Dairy Whitener 200g Pack", "cat-sm-01", "brd-sm-03", "uom-01", 130, 8, 2, 30, "890126201006", 3, 90, False),
        ("SM-007", "ID Fresh Natural Batter Wheat Dosa 1kg", "cat-sm-01", "brd-sm-10", "uom-01", 90, 10, 3, 40, "890126201007", 4, 4, True), # Low stock & Expiring!

        # Packaged Foods & Snacks (cat-sm-02)
        ("SM-008", "Maggi 2-Minute Masala Noodles Pack", "cat-sm-02", "brd-sm-03", "uom-01", 48, 15, 5, 100, "890126202008", 8, 180, False),
        ("SM-009", "Nestlé KitKat 4-Finger Chocolate 38.5g", "cat-sm-02", "brd-sm-03", "uom-01", 30, 20, 5, 150, "890126202009", 12, 120, False),
        ("SM-010", "Cadbury Dairy Milk Silk Chocolate 150g Bar", "cat-sm-02", "brd-sm-03", "uom-01", 175, 8, 2, 50, "890126202010", 3, 150, False),
        ("SM-011", "Britannia Good Day Cashew Cookies 200g", "cat-sm-02", "brd-sm-02", "uom-01", 50, 12, 4, 80, "890126202011", 7, 120, False),
        ("SM-012", "Parle-G Original Glucose Biscuits 250g", "cat-sm-02", "brd-sm-06", "uom-01", 30, 20, 5, 150, "890126202012", 10, 180, False),
        ("SM-013", "Sunfeast Dark Fantasy Choco Fills 150g", "cat-sm-02", "brd-sm-05", "uom-01", 80, 10, 3, 60, "890126202013", 5, 150, False),
        ("SM-014", "Haldiram's Nagpur Khatta Meetha Namkeen 200g", "cat-sm-02", "brd-sm-06", "uom-01", 60, 12, 4, 80, "890126202014", 6, 120, False),
        ("SM-015", "Lay's India's Magic Masala Potato Chips 50g", "cat-sm-02", "brd-sm-08", "uom-01", 20, 25, 8, 200, "890126202015", 15, 90, False),
        ("SM-016", "Doritos Nacho Cheese Tortilla Chips 50g", "cat-sm-02", "brd-sm-08", "uom-01", 30, 15, 5, 100, "890126202016", 10, 90, False),
        ("SM-017", "Kissan Mixed Fruit Jam 200g Jar", "cat-sm-02", "brd-sm-04", "uom-01", 85, 8, 2, 40, "890126202017", 4, 180, False),
        ("SM-018", "MTR Ready-To-Eat Paneer Butter Masala 300g", "cat-sm-02", "brd-sm-10", "uom-01", 120, 8, 2, 50, "890126202018", 3, 120, False),

        # Beverages & Juices (cat-sm-03)
        ("SM-019", "Real Fruit Power Mixed Fruit Juice 1L Tetra", "cat-sm-03", "brd-sm-09", "uom-05", 120, 10, 3, 60, "890126203019", 4, 18, True),
        ("SM-020", "Tropicana 100% Orange Juice 1L Tetra Pack", "cat-sm-03", "brd-sm-08", "uom-05", 130, 10, 3, 60, "890126203020", 5, 25, True),
        ("SM-021", "Coca-Cola Soft Drink 750ml PET Bottle", "cat-sm-03", "brd-sm-08", "uom-01", 40, 20, 5, 150, "890126203021", 10, 120, False),
        ("SM-022", "Pepsi Carbonated Soft Drink 750ml PET", "cat-sm-03", "brd-sm-08", "uom-01", 40, 20, 5, 150, "890126203022", 12, 120, False),
        ("SM-023", "Red Bull Energy Drink 250ml Can", "cat-sm-03", "brd-sm-08", "uom-01", 125, 8, 2, 50, "890126203023", 3, 240, False),
        ("SM-024", "Paper Boat Aamras Mango Juice 250ml Pouch", "cat-sm-03", "brd-sm-09", "uom-01", 35, 15, 5, 100, "890126203024", 8, 90, False),
        ("SM-025", "Taj Mahal Loose Leaf Black Tea 250g Box", "cat-sm-03", "brd-sm-04", "uom-01", 190, 8, 2, 40, "890126203025", 3, 365, False),
        ("SM-026", "Nescafé Classic Instant Coffee 50g Jar", "cat-sm-03", "brd-sm-03", "uom-01", 160, 8, 2, 40, "890126203026", 4, 365, False),

        # Staples, Grains & Spices (cat-sm-04)
        ("SM-027", "Aashirvaad Shuddh Chakki Whole Wheat Atta 5kg", "cat-sm-04", "brd-sm-05", "uom-03", 240, 10, 3, 50, "890126204027", 4, 90, False),
        ("SM-028", "Fortune Sunlite Refined Sunflower Oil 1L Pouch", "cat-sm-04", "brd-sm-07", "uom-05", 145, 12, 4, 60, "890126204028", 5, 180, False),
        ("SM-029", "India Gate Basmati Rice Rozzana 1kg Pack", "cat-sm-04", "brd-sm-05", "uom-03", 110, 15, 5, 80, "890126204029", 6, 365, False),
        ("SM-030", "Tata Salt Vacuum Evaporated Iodised Salt 1kg", "cat-sm-04", "brd-sm-05", "uom-01", 28, 25, 8, 200, "890126204030", 15, 730, False),
        ("SM-031", "Tata Sampann Unpolished Toor Dal 500g", "cat-sm-04", "brd-sm-05", "uom-03", 90, 15, 5, 80, "890126204031", 6, 180, False),
        ("SM-032", "Everest Royal Garam Masala Powder 100g", "cat-sm-04", "brd-sm-07", "uom-01", 82, 10, 3, 50, "890126204032", 4, 270, False),
        ("SM-033", "MDH Kashmiri Mirch Chili Powder 100g", "cat-sm-04", "brd-sm-07", "uom-01", 95, 10, 3, 50, "890126204033", 4, 270, False),
        ("SM-034", "Catch Super Red Chili Powder 100g Pack", "cat-sm-04", "brd-sm-07", "uom-01", 65, 12, 4, 60, "890126204034", 5, 270, False),

        # Personal Care & Hygiene (cat-sm-05)
        ("SM-035", "Dettol Original Soap Bar 75g (Pack of 3)", "cat-sm-05", "brd-sm-04", "uom-01", 110, 15, 5, 80, "890126205035", 6, 730, False),
        ("SM-036", "Dove Cream Beauty Bathing Bar 75g", "cat-sm-05", "brd-sm-04", "uom-01", 65, 15, 5, 80, "890126205036", 8, 730, False),
        ("SM-037", "Colgate Strong Teeth Toothpaste 150g Saver Pack", "cat-sm-05", "brd-sm-04", "uom-01", 95, 15, 5, 80, "890126205037", 7, 730, False),
        ("SM-038", "Sensodyne Repair & Protect Toothpaste 70g", "cat-sm-05", "brd-sm-04", "uom-01", 140, 10, 3, 50, "890126205038", 4, 540, False),
        ("SM-039", "Head & Shoulders Shampoo 180ml Bottle", "cat-sm-05", "brd-sm-04", "uom-01", 180, 10, 3, 50, "890126205039", 3, 730, False),
        ("SM-040", "Nivea Soft Light Moisturizing Cream 100ml", "cat-sm-05", "brd-sm-04", "uom-01", 160, 10, 3, 50, "890126205040", 4, 730, False),
        ("SM-041", "Gillette Mach3 Razor Blade Cartridges (2s)", "cat-sm-05", "brd-sm-04", "uom-01", 350, 8, 2, 40, "890126205041", 2, 1095, False),
        ("SM-042", "Whisper Choice Ultra XL Sanitary Pads (6s)", "cat-sm-05", "brd-sm-04", "uom-01", 50, 20, 5, 100, "890126205042", 10, 1095, False),
        ("SM-043", "Pampers Baby Diapers Pants Large (10s)", "cat-sm-05", "brd-sm-04", "uom-01", 220, 8, 2, 40, "890126205043", 3, 1095, False),

        # Household & Cleaning Supplies (cat-sm-06)
        ("SM-044", "Surf Excel Easy Wash Detergent Powder 1kg", "cat-sm-06", "brd-sm-04", "uom-03", 140, 12, 4, 60, "890126206044", 5, 730, False),
        ("SM-045", "Ariel Matic Front Load Detergent Powder 1kg", "cat-sm-06", "brd-sm-04", "uom-01", 240, 10, 3, 50, "890126206045", 3, 730, False),
        ("SM-046", "Vim Dishwash Liquid Gel Lemon 250ml Bottle", "cat-sm-06", "brd-sm-04", "uom-01", 60, 15, 5, 80, "890126206046", 8, 540, False),
        ("SM-047", "Harpic Power Plus Toilet Cleaner 500ml", "cat-sm-06", "brd-sm-04", "uom-01", 115, 12, 4, 60, "890126206047", 5, 730, False),
        ("SM-048", "Lizol Surface Floor Cleaner Citrus 500ml", "cat-sm-06", "brd-sm-04", "uom-01", 110, 12, 4, 60, "890126206048", 5, 730, False),

        # Frozen & Fresh Produce (cat-sm-07)
        ("SM-049", "McCain French Fries Crispy 375g Frozen Bag", "cat-sm-07", "brd-sm-10", "uom-01", 110, 10, 3, 50, "890126207049", 4, 22, True),
        ("SM-050", "Kwality Wall's Vanilla Ice Cream Tub 500ml", "cat-sm-07", "brd-sm-10", "uom-01", 135, 10, 3, 50, "890126207050", 4, 45, False)
    ]

    TARGET_TOTAL_VALUE = 18000.0
    current_sum = 0
    calculated_products = []

    for idx, p in enumerate(products_raw):
        code, name, cat_id, brd_id, uom_id, price, reorder, min_s, max_s, barcode, qty, exp_days, is_expiring = p
        if idx < len(products_raw) - 1:
            item_val = qty * price
            current_sum += item_val
            calculated_products.append((code, name, cat_id, brd_id, uom_id, price, reorder, min_s, max_s, barcode, qty, exp_days, is_expiring))
        else:
            remaining_val = TARGET_TOTAL_VALUE - current_sum
            adj_price = 100.0
            adj_qty = round(remaining_val / adj_price, 2)
            calculated_products.append((code, name, cat_id, brd_id, uom_id, adj_price, reorder, min_s, max_s, barcode, adj_qty, exp_days, is_expiring))

    db["items"] = [i for i in db.get("items", []) if i.get("created_by") != DEMO_USER]
    db["inventory_balances"] = [b for b in db.get("inventory_balances", []) if b.get("created_by") != DEMO_USER]

    for idx, p in enumerate(calculated_products):
        code, name, cat_id, brd_id, uom_id, price, reorder, min_s, max_s, barcode, available_qty, exp_days, is_expiring = p
        item_id = f"itm-sm-{idx+1:03d}"

        db["items"].append({
            "id": item_id,
            "item_code": code,
            "name": name,
            "category_id": cat_id,
            "brand_id": brd_id,
            "uom_id": uom_id,
            "unit_price": price,
            "valuation_rate": price,
            "reorder_level": reorder,
            "min_stock": min_s,
            "max_stock": max_s,
            "available_qty": available_qty,
            "on_hand_qty": available_qty,
            "barcode": barcode,
            "status": "Active",
            "description": f"Supermarket SKU {name} for retail shelves",
            "is_expiring": is_expiring,
            "expiry_days": exp_days if is_expiring else None,
            "expiry_date": (now_dt + timedelta(days=exp_days)).strftime("%Y-%m-%d") if is_expiring else None,
            "created_by": DEMO_USER,
            "company_name": DEMO_COMPANY,
            "is_demo": IS_DEMO
        })

        bal_id = f"bal-sm-{idx+1:03d}"
        reserved_qty = 1 if available_qty > 5 else 0
        total_qty = available_qty + reserved_qty

        db["inventory_balances"].append({
            "id": bal_id,
            "item_id": item_id,
            "item_code": code,
            "item_name": name,
            "warehouse_id": "wh-01" if idx % 2 == 0 else "wh-02",
            "location_id": "loc-101" if idx % 2 == 0 else "loc-201",
            "quantity": total_qty,
            "on_hand_qty": total_qty,
            "reserved_qty": reserved_qty,
            "available_qty": available_qty,
            "batch_number": f"BAT-SM-2026-{idx+1:03d}",
            "unit_cost": price,
            "is_expiring": is_expiring,
            "expiry_days": exp_days if is_expiring else None,
            "expiry_date": (now_dt + timedelta(days=exp_days)).strftime("%Y-%m-%d") if is_expiring else None,
            "created_by": DEMO_USER,
            "company_name": DEMO_COMPANY,
            "is_demo": IS_DEMO
        })

    # -------------------------------------------------------------------------
    # 8. Indents (sec-11)
    # -------------------------------------------------------------------------
    db["indents"] = [i for i in db.get("indents", []) if i.get("created_by") != DEMO_USER]
    sm_indents = [
        {"id": "ind-sm-01", "indent_number": "IND-2026-00101", "requester_name": "Ashin Demo Administrator", "department_id": "dept-sm-01", "department_name": "Fresh Foods & Dairy Dept", "status": "Pending Approval", "urgency": "High", "created_at": now_str, "total_value": 4500, "reason": "Restock Dairy, Milk & Butter for weekend footfall", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "ind-sm-02", "indent_number": "IND-2026-00102", "requester_name": "Suresh Kumar", "department_id": "dept-sm-02", "department_name": "Packaged Grocery & Beverages", "status": "Approved", "urgency": "Medium", "created_at": now_str, "total_value": 6200, "reason": "Atta, Cooking Oils & Rice bulk restocking", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "ind-sm-03", "indent_number": "IND-2026-00103", "requester_name": "Priya Menon", "department_id": "dept-sm-02", "department_name": "Packaged Grocery & Beverages", "status": "Processing", "urgency": "High", "created_at": now_str, "total_value": 2800, "reason": "Soft drinks & Beverage chilled rack replenishment", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "ind-sm-04", "indent_number": "IND-2026-00104", "requester_name": "Rajesh Patel", "department_id": "dept-sm-03", "department_name": "Personal Care & Household Cleaning", "status": "Submitted", "urgency": "Normal", "created_at": now_str, "total_value": 1900, "reason": "Dettol & Personal Care detergent replenishment", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "ind-sm-05", "indent_number": "IND-2026-00105", "requester_name": "Vikram Verma", "department_id": "dept-sm-04", "department_name": "Store Operations & Maintenance", "status": "Completed", "urgency": "High", "created_at": now_str, "total_value": 3100, "reason": "Packaging bags & POS paper rolls", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["indents"].extend(sm_indents)

    # -------------------------------------------------------------------------
    # 9. RFQs (sec-14) & Quotations (sec-15)
    # -------------------------------------------------------------------------
    db["rfqs"] = [r for r in db.get("rfqs", []) if r.get("created_by") != DEMO_USER]
    sm_rfqs = [
        {"id": "rfq-sm-01", "rfq_number": "RFQ-2026-00201", "title": "Fresh Milk & Dairy Bulk Sourcing Q3", "status": "Sent to Suppliers", "due_date": (now_dt + timedelta(days=7)).strftime("%Y-%m-%d"), "created_at": now_str, "suppliers_count": 3, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "rfq-sm-02", "rfq_number": "RFQ-2026-00202", "title": "FMCG Beverages & Soft Drinks Supply Contract", "status": "Published", "due_date": (now_dt + timedelta(days=10)).strftime("%Y-%m-%d"), "created_at": now_str, "suppliers_count": 2, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "rfq-sm-03", "rfq_number": "RFQ-2026-00203", "title": "Packaging & Dispatch Corrugated Crates", "status": "Draft", "due_date": (now_dt + timedelta(days=12)).strftime("%Y-%m-%d"), "created_at": now_str, "suppliers_count": 4, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["rfqs"].extend(sm_rfqs)

    db["quotations"] = [q for q in db.get("quotations", []) if q.get("created_by") != DEMO_USER]
    sm_quotes = [
        {"id": "qte-sm-01", "quotation_number": "QT-2026-001", "rfq_number": "RFQ-2026-00201", "supplier_name": "GCMMF Amul Milk Wholesale", "total_amount": 5400, "delivery_lead_days": 2, "is_l1_recommended": True, "status": "Evaluated L1", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "qte-sm-02", "quotation_number": "QT-2026-002", "rfq_number": "RFQ-2026-00201", "supplier_name": "Nestlé India FMCG Distributors", "total_amount": 5800, "delivery_lead_days": 4, "is_l1_recommended": False, "status": "Evaluated L2", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["quotations"].extend(sm_quotes)

    # -------------------------------------------------------------------------
    # 10. Purchase Orders (sec-16)
    # -------------------------------------------------------------------------
    db["purchase_orders"] = [p for p in db.get("purchase_orders", []) if p.get("created_by") != DEMO_USER]
    sm_pos = [
        {"id": "po-sm-01", "po_number": "PO-2026-00301", "supplier_id": "sup-sm-01", "supplier_name": "GCMMF Amul Milk & Dairy Wholesale", "warehouse_id": "wh-01", "status": "Approved", "created_at": now_str, "delivery_date": (now_dt + timedelta(days=2)).strftime("%Y-%m-%d"), "total_amount": 5400, "tax_amount": 270, "grand_total": 5670, "items_count": 100, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "po-sm-02", "po_number": "PO-2026-00302", "supplier_id": "sup-sm-02", "supplier_name": "Nestlé India FMCG Distributors", "warehouse_id": "wh-01", "status": "Processing", "created_at": now_str, "delivery_date": (now_dt + timedelta(days=4)).strftime("%Y-%m-%d"), "total_amount": 8500, "tax_amount": 1530, "grand_total": 10030, "items_count": 250, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "po-sm-03", "po_number": "PO-2026-00303", "supplier_id": "sup-sm-03", "supplier_name": "Hindustan Unilever Wholesale Depot", "warehouse_id": "wh-02", "status": "Issued", "created_at": now_str, "delivery_date": (now_dt + timedelta(days=5)).strftime("%Y-%m-%d"), "total_amount": 6200, "tax_amount": 1116, "grand_total": 7316, "items_count": 180, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "po-sm-04", "po_number": "PO-2026-00304", "supplier_id": "sup-sm-05", "supplier_name": "ITC Agri & Staples Wholesale", "warehouse_id": "wh-01", "status": "Draft", "created_at": now_str, "delivery_date": (now_dt + timedelta(days=6)).strftime("%Y-%m-%d"), "total_amount": 9200, "tax_amount": 460, "grand_total": 9660, "items_count": 150, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["purchase_orders"].extend(sm_pos)

    # -------------------------------------------------------------------------
    # 11. Goods Receipt Notes (GRNs) (sec-17)
    # -------------------------------------------------------------------------
    db["goods_receipts"] = [g for g in db.get("goods_receipts", []) if g.get("created_by") != DEMO_USER]
    sm_grns = [
        {"id": "grn-sm-01", "grn_number": "GRN-2026-00401", "po_number": "PO-2026-00301", "supplier_name": "GCMMF Amul Milk & Dairy Wholesale", "warehouse_id": "wh-01", "status": "Under Quality Inspection", "received_date": now_str, "total_items": 4, "total_value": 5400, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "grn-sm-02", "grn_number": "GRN-2026-00402", "po_number": "PO-2026-00303", "supplier_name": "Hindustan Unilever Wholesale Depot", "warehouse_id": "wh-02", "status": "Pending Verification", "received_date": now_str, "total_items": 8, "total_value": 6200, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "grn-sm-03", "grn_number": "GRN-2026-00403", "po_number": "PO-2026-00304", "supplier_name": "Britannia Bakery Products Direct", "warehouse_id": "wh-01", "status": "Draft", "received_date": now_str, "total_items": 3, "total_value": 3100, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["goods_receipts"].extend(sm_grns)

    # -------------------------------------------------------------------------
    # 12. Quality Inspection (sec-18)
    # -------------------------------------------------------------------------
    db["quality_inspections"] = [q for q in db.get("quality_inspections", []) if q.get("created_by") != DEMO_USER]
    sm_qi = [
        {
            "id": "qi-sm-01",
            "inspection_reference": "QI-2026-00501",
            "grn_id": "grn-sm-01",
            "grn_reference": "GRN-2026-00401",
            "item_id": "itm-sm-001",
            "item_code": "SM-001",
            "item_name": "Amul Taaza Toned Fresh Milk 1L Pouch",
            "inspected_by": "Suresh Kumar",
            "inspection_date": now_str,
            "accepted_qty": 50,
            "rejected_qty": 2,
            "inspection_outcome": "Accepted with deviation",
            "remarks": "Temperature test passed at 4 degrees C. 2 pouches leaked.",
            "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO
        },
        {
            "id": "qi-sm-02",
            "inspection_reference": "QI-2026-00502",
            "grn_id": "grn-sm-02",
            "grn_reference": "GRN-2026-00402",
            "item_id": "itm-sm-005",
            "item_code": "SM-005",
            "item_name": "Britannia 100% Whole Wheat Bread 400g",
            "inspected_by": "Ashin Demo Administrator",
            "inspection_date": now_str,
            "accepted_qty": 30,
            "rejected_qty": 0,
            "inspection_outcome": "Accepted",
            "remarks": "Freshness date and seal verified OK.",
            "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO
        }
    ]
    db["quality_inspections"].extend(sm_qi)

    # -------------------------------------------------------------------------
    # 13. Stock Ledger (sec-19)
    # -------------------------------------------------------------------------
    db["inventory_ledger"] = [l for l in db.get("inventory_ledger", []) if l.get("created_by") != DEMO_USER]
    sm_ledger = [
        {"id": "led-sm-01", "transaction_type": "PURCHASE_RECEIPT", "reference_no": "GRN-2026-00401", "date": now_str, "item_code": "SM-001", "item_name": "Amul Taaza Toned Milk 1L", "quantity": "+50 Pcs", "status": "Posted", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "led-sm-02", "transaction_type": "STOCK_ISSUE", "reference_no": "ISS-2026-00601", "date": now_str, "item_code": "SM-005", "item_name": "Britannia Whole Wheat Bread", "quantity": "-10 Pcs", "status": "Completed", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "led-sm-03", "transaction_type": "TRANSFER_OUT", "reference_no": "TRN-2026-00901", "date": now_str, "item_code": "SM-021", "item_name": "Coca-Cola Soft Drink 750ml", "quantity": "-20 Pcs", "status": "In Transit", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["inventory_ledger"].extend(sm_ledger)

    # -------------------------------------------------------------------------
    # 14. Stock Issues (sec-21)
    # -------------------------------------------------------------------------
    db["stock_issues"] = [i for i in db.get("stock_issues", []) if i.get("created_by") != DEMO_USER]
    sm_issues = [
        {"id": "iss-sm-01", "issue_number": "ISS-2026-00601", "department_id": "dept-sm-01", "warehouse_id": "wh-01", "issued_to": "Kochi Supermarket Rack 4", "status": "Issued & Verified", "created_at": now_str, "total_qty": 15, "total_value": 850, "purpose": "Retail Floor Shelf Replenishment", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "iss-sm-02", "issue_number": "ISS-2026-00602", "department_id": "dept-sm-02", "warehouse_id": "wh-02", "issued_to": "Express Billing Counters", "status": "Issued", "created_at": now_str, "total_qty": 30, "total_value": 1400, "purpose": "Carry Bags & Promotional Pack Issue", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["stock_issues"].extend(sm_issues)

    # -------------------------------------------------------------------------
    # 15. Stock Returns (sec-22)
    # -------------------------------------------------------------------------
    db["stock_returns"] = [r for r in db.get("stock_returns", []) if r.get("created_by") != DEMO_USER]
    sm_returns = [
        {"id": "ret-sm-01", "return_number": "RET-2026-00701", "department_id": "dept-sm-01", "warehouse_id": "wh-01", "status": "Returned to Stock", "created_at": now_str, "returned_qty": 3, "returned_value": 162, "reason": "Unsold Bakery items returned from shelf", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["stock_returns"].extend(sm_returns)

    # -------------------------------------------------------------------------
    # 16. Supplier Returns (sec-23)
    # -------------------------------------------------------------------------
    db["supplier_returns"] = [s for s in db.get("supplier_returns", []) if s.get("created_by") != DEMO_USER]
    sm_sup_returns = [
        {"id": "sret-sm-01", "return_number": "SRET-2026-00801", "supplier_name": "GCMMF Amul Milk Wholesale", "warehouse_id": "wh-01", "status": "Dispatched to Vendor", "created_at": now_str, "rejected_qty": 2, "total_refund_value": 108, "reason": "Leaked milk pouches detected during quality inspection", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["supplier_returns"].extend(sm_sup_returns)

    # -------------------------------------------------------------------------
    # 17. Stock Transfers (sec-24)
    # -------------------------------------------------------------------------
    db["stock_transfers"] = [t for t in db.get("stock_transfers", []) if t.get("created_by") != DEMO_USER]
    sm_transfers = [
        {"id": "trn-sm-01", "transfer_number": "TRN-2026-00901", "from_warehouse_id": "wh-01", "to_warehouse_id": "wh-02", "status": "In Transit", "created_at": now_str, "total_qty": 25, "reason": "Transfer beverage stock to Cold Chain Hub", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["stock_transfers"].extend(sm_transfers)

    # -------------------------------------------------------------------------
    # 18. Stock Adjustments (sec-25)
    # -------------------------------------------------------------------------
    db["stock_adjustments"] = [a for a in db.get("stock_adjustments", []) if a.get("created_by") != DEMO_USER]
    sm_adjustments = [
        {"id": "adj-sm-01", "adjustment_number": "ADJ-2026-01001", "warehouse_id": "wh-01", "adjustment_type": "POSITIVE", "quantity": 5, "reason": "Physical count audit surplus found during weekly check", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["stock_adjustments"].extend(sm_adjustments)

    # -------------------------------------------------------------------------
    # 19. Physical Stock Verification (sec-26)
    # -------------------------------------------------------------------------
    db["stock_count_sessions"] = [s for s in db.get("stock_count_sessions", []) if s.get("created_by") != DEMO_USER]
    sm_sessions = [
        {"id": "ses-sm-01", "session_number": "SESSION-2026-001", "warehouse_id": "wh-01", "status": "In Progress", "audit_date": now_str, "auditor_name": "Suresh Kumar", "variance_items": 2, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["stock_count_sessions"].extend(sm_sessions)

    # -------------------------------------------------------------------------
    # 20. Reservation Management (sec-27)
    # -------------------------------------------------------------------------
    db["stock_reservations"] = [r for r in db.get("stock_reservations", []) if r.get("created_by") != DEMO_USER]
    sm_res = [
        {"id": "res-sm-01", "reservation_number": "RES-2026-001", "item_code": "SM-001", "item_name": "Amul Taaza Milk 1L", "reserved_qty": 5, "reserved_for": "Weekend Supermarket Promotion", "expiry_date": (now_dt + timedelta(days=3)).strftime("%Y-%m-%d"), "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["stock_reservations"].extend(sm_res)

    # -------------------------------------------------------------------------
    # 21. Asset Tracking (sec-28)
    # -------------------------------------------------------------------------
    db["assets"] = [a for a in db.get("assets", []) if a.get("created_by") != DEMO_USER]
    sm_assets = [
        {"id": "ast-sm-01", "asset_tag": "POS-TERM-01", "name": "Express Billing POS Terminal 1", "category": "Retail POS Equipment", "assigned_to": "Cashier Desk 1", "department": "Store Operations", "purchase_cost": 45000, "status": "Active / Assigned", "barcode": "AST8901234501", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "ast-sm-02", "asset_tag": "BAR-SCN-02", "name": "Honeywell Laser Scanner Handheld", "category": "Retail POS Equipment", "assigned_to": "Billing Counter 2", "department": "Store Operations", "purchase_cost": 4500, "status": "Active / Assigned", "barcode": "AST8901234502", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "ast-sm-03", "asset_tag": "COLD-CHILL-03", "name": "Voltas Commercial Glass Door Display Chiller", "category": "Refrigeration Plant", "assigned_to": "Fresh Dairy Isle", "department": "Fresh Foods & Dairy", "purchase_cost": 125000, "status": "Active / In-Store", "barcode": "AST8901234503", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["assets"].extend(sm_assets)

    # -------------------------------------------------------------------------
    # 22. Audit Logs (sec-31)
    # -------------------------------------------------------------------------
    db["audit_logs"] = [a for a in db.get("audit_logs", []) if a.get("created_by") != DEMO_USER]
    sm_audit = [
        {"id": "aud-sm-01", "timestamp": now_str, "user_id": "usr-ashin", "user_name": "Ashin Demo Administrator", "action": "LOGIN_SUCCESS", "category": "Authentication", "module": "Authentication", "record_id": "usr-ashin", "ip_address": "127.0.0.1", "device_browser": "Chrome / Windows", "details": "User Ashin Demo Administrator signed in successfully.", "reason": "Demo Login", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "aud-sm-02", "timestamp": now_str, "user_id": "usr-ashin", "user_name": "Ashin Demo Administrator", "action": "STOCK_UPDATED", "category": "Stock Operations", "module": "Current Stock", "record_id": "SM-001", "ip_address": "127.0.0.1", "device_browser": "Chrome / Windows", "details": "Updated stock levels for Supermarket SKUs.", "reason": "Stock Audit Check", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["audit_logs"].extend(sm_audit)

    # Save all 35 modules data directly to PostgreSQL database via .env
    save_db()

    print("=================================================================")
    print(" SUCCESS! Full Supermarket Demo Data Populated Across 35 Modules!")
    print(f" Target User: {DEMO_USER}")
    print(f" Saved to PostgreSQL Table State successfully!")
    print("=================================================================")

if __name__ == "__main__":
    seed_full_35_modules_demo()
