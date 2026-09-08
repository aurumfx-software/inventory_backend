import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database_store import db, save_db

def seed_supermarket_demo():
    print("=================================================================")
    print(" Populating 50 Supermarket Items (Total Stock Value = INR 18,000)...")
    print("=================================================================")

    DEMO_USER = "ashina123@gmail.com"
    DEMO_COMPANY = "Ashin Enterprise Demo"
    IS_DEMO = True

    # 1. Supermarket Categories
    sm_categories = [
        {"id": "cat-sm-01", "name": "Dairy, Bakery & Fresh Produce", "code": "FRESH-DAIRY", "tax_rate_id": "tax-5", "description": "Fresh Milk, Butter, Cheese, Bread & Farm Vegetables", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-02", "name": "Packaged Foods & Snacks", "code": "SNACK-PKG", "tax_rate_id": "tax-12", "description": "Biscuits, Chocolates, Chips & Ready-to-Eat Snacks", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-03", "name": "Beverages & Cold Drinks", "code": "BEV-DRINK", "tax_rate_id": "tax-18", "description": "Soft Drinks, Fruit Juices, Energy Drinks & Teas", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-04", "name": "Staples, Grains & Spices", "code": "STAPLE-GRN", "tax_rate_id": "tax-5", "description": "Atta, Rice, Pulses, Cooking Oils & Masalas", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-05", "name": "Personal Care & Hygiene", "code": "CARE-HYG", "tax_rate_id": "tax-18", "description": "Soaps, Shampoos, Toothpastes & Cosmetics", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-06", "name": "Household & Cleaning Supplies", "code": "CLEAN-HOU", "tax_rate_id": "tax-18", "description": "Detergents, Surface Cleaners & Dishwash Gels", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "cat-sm-07", "name": "Frozen Foods & Ice Creams", "code": "FRZN-ICE", "tax_rate_id": "tax-18", "description": "Frozen Fries, Ready Meals & Ice Cream Tubs", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]

    existing_cat_ids = {c["id"] for c in db.get("item_categories", [])}
    for cat in sm_categories:
        if cat["id"] not in existing_cat_ids:
            db["item_categories"].append(cat)

    # 2. Supermarket Brands
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

    existing_brd_ids = {b["id"] for b in db.get("brands", [])}
    for brd in sm_brands:
        if brd["id"] not in existing_brd_ids:
            db["brands"].append(brd)

    # 3. Supermarket Suppliers
    sm_suppliers = [
        {"id": "sup-sm-01", "code": "SUP-AMUL-01", "name": "GCMMF Amul Milk & Dairy Wholesale", "contact_person": "Vikram Patel", "email": "supply@amul.coop", "phone": "9825012345", "city": "Anand / Bangalore", "grade": "A+", "rating": 4.9, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "sup-sm-02", "code": "SUP-NESTLE-02", "name": "Nestlé India FMCG Distributors", "contact_person": "Meera Sen", "email": "orders@in.nestle.com", "phone": "9810098765", "city": "Bangalore", "grade": "A+", "rating": 4.8, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "sup-sm-03", "code": "SUP-HUL-03", "name": "Hindustan Unilever Wholesale Depot", "contact_person": "Rajesh Gupta", "email": "depot.hul@unilever.com", "phone": "9845011223", "city": "Kochi", "grade": "A+", "rating": 4.9, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "sup-sm-04", "code": "SUP-BRIT-04", "name": "Britannia Bakery Products Direct", "contact_person": "Anil Nair", "email": "sales@britindia.com", "phone": "9895033445", "city": "Kochi", "grade": "A", "rating": 4.7, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "sup-sm-05", "code": "SUP-ITC-05", "name": "ITC Agri & Staples Wholesale", "contact_person": "Karan Singhania", "email": "fmcg@itc.in", "phone": "9830055667", "city": "Mumbai", "grade": "A+", "rating": 4.9, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "sup-sm-06", "code": "SUP-BEV-06", "name": "United Beverage Bottlers (Coke & Pepsi)", "contact_person": "Deepak Roy", "email": "orders@beveragebottlers.in", "phone": "9871144556", "city": "Bangalore", "grade": "A", "rating": 4.6, "status": "Active", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]

    existing_sup_ids = {s["id"] for s in db.get("suppliers", [])}
    for sup in sm_suppliers:
        if sup["id"] not in existing_sup_ids:
            db["suppliers"].append(sup)

    # 4. 50 Supermarket Products Meta Definition
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
        ("SM-008", "Maggi 2-Minute Masala Noodles Pack", "cat-sm-02", "brd-sm-03", "uom-01", 48, 15, 5, 100, "890126202008", 8, 180, False), # Low stock!
        ("SM-009", "Nestlé KitKat 4-Finger Chocolate 38.5g", "cat-sm-02", "brd-sm-03", "uom-01", 30, 20, 5, 150, "890126202009", 12, 120, False), # Low stock!
        ("SM-010", "Cadbury Dairy Milk Silk Chocolate 150g Bar", "cat-sm-02", "brd-sm-03", "uom-01", 175, 8, 2, 50, "890126202010", 3, 150, False), # Low stock!
        ("SM-011", "Britannia Good Day Cashew Cookies 200g", "cat-sm-02", "brd-sm-02", "uom-01", 50, 12, 4, 80, "890126202011", 7, 120, False), # Low stock!
        ("SM-012", "Parle-G Original Glucose Biscuits 250g", "cat-sm-02", "brd-sm-06", "uom-01", 30, 20, 5, 150, "890126202012", 10, 180, False), # Low stock!
        ("SM-013", "Sunfeast Dark Fantasy Choco Fills 150g", "cat-sm-02", "brd-sm-05", "uom-01", 80, 10, 3, 60, "890126202013", 5, 150, False), # Low stock!
        ("SM-014", "Haldiram's Nagpur Khatta Meetha Namkeen 200g", "cat-sm-02", "brd-sm-06", "uom-01", 60, 12, 4, 80, "890126202014", 6, 120, False), # Low stock!
        ("SM-015", "Lay's India's Magic Masala Potato Chips 50g", "cat-sm-02", "brd-sm-08", "uom-01", 20, 25, 8, 200, "890126202015", 15, 90, False), # Low stock!
        ("SM-016", "Doritos Nacho Cheese Tortilla Chips 50g", "cat-sm-02", "brd-sm-08", "uom-01", 30, 15, 5, 100, "890126202016", 10, 90, False), # Low stock!
        ("SM-017", "Kissan Mixed Fruit Jam 200g Jar", "cat-sm-02", "brd-sm-04", "uom-01", 85, 8, 2, 40, "890126202017", 4, 180, False), # Low stock!
        ("SM-018", "MTR Ready-To-Eat Paneer Butter Masala 300g", "cat-sm-02", "brd-sm-10", "uom-01", 120, 8, 2, 50, "890126202018", 3, 120, False), # Low stock!

        # Beverages & Juices (cat-sm-03)
        ("SM-019", "Real Fruit Power Mixed Fruit Juice 1L Tetra", "cat-sm-03", "brd-sm-09", "uom-05", 120, 10, 3, 60, "890126203019", 4, 18, True), # Low stock & Expiring!
        ("SM-020", "Tropicana 100% Orange Juice 1L Tetra Pack", "cat-sm-03", "brd-sm-08", "uom-05", 130, 10, 3, 60, "890126203020", 5, 25, True), # Low stock & Expiring!
        ("SM-021", "Coca-Cola Soft Drink 750ml PET Bottle", "cat-sm-03", "brd-sm-08", "uom-01", 40, 20, 5, 150, "890126203021", 10, 120, False), # Low stock!
        ("SM-022", "Pepsi Carbonated Soft Drink 750ml PET", "cat-sm-03", "brd-sm-08", "uom-01", 40, 20, 5, 150, "890126203022", 12, 120, False), # Low stock!
        ("SM-023", "Red Bull Energy Drink 250ml Can", "cat-sm-03", "brd-sm-08", "uom-01", 125, 8, 2, 50, "890126203023", 3, 240, False), # Low stock!
        ("SM-024", "Paper Boat Aamras Mango Juice 250ml Pouch", "cat-sm-03", "brd-sm-09", "uom-01", 35, 15, 5, 100, "890126203024", 8, 90, False), # Low stock!
        ("SM-025", "Taj Mahal Loose Leaf Black Tea 250g Box", "cat-sm-03", "brd-sm-04", "uom-01", 190, 8, 2, 40, "890126203025", 3, 365, False), # Low stock!
        ("SM-026", "Nescafé Classic Instant Coffee 50g Jar", "cat-sm-03", "brd-sm-03", "uom-01", 160, 8, 2, 40, "890126203026", 4, 365, False), # Low stock!

        # Staples, Grains & Spices (cat-sm-04)
        ("SM-027", "Aashirvaad Shuddh Chakki Whole Wheat Atta 5kg", "cat-sm-04", "brd-sm-05", "uom-03", 240, 10, 3, 50, "890126204027", 4, 90, False), # Low stock!
        ("SM-028", "Fortune Sunlite Refined Sunflower Oil 1L Pouch", "cat-sm-04", "brd-sm-07", "uom-05", 145, 12, 4, 60, "890126204028", 5, 180, False), # Low stock!
        ("SM-029", "India Gate Basmati Rice Rozzana 1kg Pack", "cat-sm-04", "brd-sm-05", "uom-03", 110, 15, 5, 80, "890126204029", 6, 365, False), # Low stock!
        ("SM-030", "Tata Salt Vacuum Evaporated Iodised Salt 1kg", "cat-sm-04", "brd-sm-05", "uom-01", 28, 25, 8, 200, "890126204030", 15, 730, False), # Low stock!
        ("SM-031", "Tata Sampann Unpolished Toor Dal 500g", "cat-sm-04", "brd-sm-05", "uom-03", 90, 15, 5, 80, "890126204031", 6, 180, False), # Low stock!
        ("SM-032", "Everest Royal Garam Masala Powder 100g", "cat-sm-04", "brd-sm-07", "uom-01", 82, 10, 3, 50, "890126204032", 4, 270, False), # Low stock!
        ("SM-033", "MDH Kashmiri Mirch Chili Powder 100g", "cat-sm-04", "brd-sm-07", "uom-01", 95, 10, 3, 50, "890126204033", 4, 270, False), # Low stock!
        ("SM-034", "Catch Super Red Chili Powder 100g Pack", "cat-sm-04", "brd-sm-07", "uom-01", 65, 12, 4, 60, "890126204034", 5, 270, False), # Low stock!

        # Personal Care & Hygiene (cat-sm-05)
        ("SM-035", "Dettol Original Soap Bar 75g (Pack of 3)", "cat-sm-05", "brd-sm-04", "uom-01", 110, 15, 5, 80, "890126205035", 6, 730, False), # Low stock!
        ("SM-036", "Dove Cream Beauty Bathing Bar 75g", "cat-sm-05", "brd-sm-04", "uom-01", 65, 15, 5, 80, "890126205036", 8, 730, False), # Low stock!
        ("SM-037", "Colgate Strong Teeth Toothpaste 150g Saver Pack", "cat-sm-05", "brd-sm-04", "uom-01", 95, 15, 5, 80, "890126205037", 7, 730, False), # Low stock!
        ("SM-038", "Sensodyne Repair & Protect Toothpaste 70g", "cat-sm-05", "brd-sm-04", "uom-01", 140, 10, 3, 50, "890126205038", 4, 540, False), # Low stock!
        ("SM-039", "Head & Shoulders Shampoo 180ml Bottle", "cat-sm-05", "brd-sm-04", "uom-01", 180, 10, 3, 50, "890126205039", 3, 730, False), # Low stock!
        ("SM-040", "Nivea Soft Light Moisturizing Cream 100ml", "cat-sm-05", "brd-sm-04", "uom-01", 160, 10, 3, 50, "890126205040", 4, 730, False), # Low stock!
        ("SM-041", "Gillette Mach3 Razor Blade Cartridges (2s)", "cat-sm-05", "brd-sm-04", "uom-01", 350, 8, 2, 40, "890126205041", 2, 1095, False), # Low stock!
        ("SM-042", "Whisper Choice Ultra XL Sanitary Pads (6s)", "cat-sm-05", "brd-sm-04", "uom-01", 50, 20, 5, 100, "890126205042", 10, 1095, False), # Low stock!
        ("SM-043", "Pampers Baby Diapers Pants Large (10s)", "cat-sm-05", "brd-sm-04", "uom-01", 220, 8, 2, 40, "890126205043", 3, 1095, False), # Low stock!

        # Household & Cleaning Supplies (cat-sm-06)
        ("SM-044", "Surf Excel Easy Wash Detergent Powder 1kg", "cat-sm-06", "brd-sm-04", "uom-03", 140, 12, 4, 60, "890126206044", 5, 730, False), # Low stock!
        ("SM-045", "Ariel Matic Front Load Detergent Powder 1kg", "cat-sm-06", "brd-sm-04", "uom-01", 240, 10, 3, 50, "890126206045", 3, 730, False), # Low stock!
        ("SM-046", "Vim Dishwash Liquid Gel Lemon 250ml Bottle", "cat-sm-06", "brd-sm-04", "uom-01", 60, 15, 5, 80, "890126206046", 8, 540, False), # Low stock!
        ("SM-047", "Harpic Power Plus Toilet Cleaner 500ml", "cat-sm-06", "brd-sm-04", "uom-01", 115, 12, 4, 60, "890126206047", 5, 730, False), # Low stock!
        ("SM-048", "Lizol Surface Floor Cleaner Citrus 500ml", "cat-sm-06", "brd-sm-04", "uom-01", 110, 12, 4, 60, "890126206048", 5, 730, False), # Low stock!

        # Frozen & Fresh Produce (cat-sm-07)
        ("SM-049", "McCain French Fries Crispy 375g Frozen Bag", "cat-sm-07", "brd-sm-10", "uom-01", 110, 10, 3, 50, "890126207049", 4, 22, True), # Low stock & Expiring!
        ("SM-050", "Kwality Wall's Vanilla Ice Cream Tub 500ml", "cat-sm-07", "brd-sm-10", "uom-01", 135, 10, 3, 50, "890126207050", 4, 45, False) # Low stock!
    ]

    # Calculate exact total sum of available_qty * unit_price for the first 49 items
    # and adjust item 50 so that TOTAL SUM IS EXACTLY ₹18,000!
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
            # Last item (SM-050 Kwality Wall's Ice Cream): adjust quantity & price so TOTAL SUM == 18,000!
            remaining_val = TARGET_TOTAL_VALUE - current_sum
            adj_price = 100.0
            adj_qty = round(remaining_val / adj_price, 2)
            if adj_qty <= 0:
                adj_price = 50.0
                adj_qty = round(remaining_val / adj_price, 2)
            
            calculated_products.append((code, name, cat_id, brd_id, uom_id, adj_price, reorder, min_s, max_s, barcode, adj_qty, exp_days, is_expiring))

    # Wipe existing demo items & balances for ashina123
    db["items"] = [i for i in db.get("items", []) if i.get("created_by") != DEMO_USER]
    db["inventory_balances"] = [b for b in db.get("inventory_balances", []) if b.get("created_by") != DEMO_USER]

    now_dt = datetime.now()
    final_stock_val = 0.0

    for idx, p in enumerate(calculated_products):
        code, name, cat_id, brd_id, uom_id, price, reorder, min_s, max_s, barcode, available_qty, exp_days, is_expiring = p
        item_id = f"itm-sm-{idx+1:03d}"
        item_value = available_qty * price
        final_stock_val += item_value

        # Create Item Master Record
        item_obj = {
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
        }
        db["items"].append(item_obj)

        # Create Inventory Balance Record
        bal_id = f"bal-sm-{idx+1:03d}"
        reserved_qty = 1 if available_qty > 5 else 0
        total_qty = available_qty + reserved_qty

        balance_obj = {
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
        }
        db["inventory_balances"].append(balance_obj)

    # 5. Supermarket Indents (Ongoing Indents)
    db["indents"] = [i for i in db.get("indents", []) if i.get("created_by") != DEMO_USER]
    sm_indents = [
        {"id": "ind-sm-01", "indent_number": "IND-2026-00101", "requester_name": "Ashin Demo Administrator", "department_id": "dept-01", "status": "Pending Approval", "urgency": "High", "created_at": now_dt.strftime("%Y-%m-%d"), "total_value": 4500, "reason": "Restock Dairy, Milk & Butter for weekend footfall", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "ind-sm-02", "indent_number": "IND-2026-00102", "requester_name": "Suresh Kumar", "department_id": "dept-02", "status": "Approved", "urgency": "Medium", "created_at": now_dt.strftime("%Y-%m-%d"), "total_value": 6200, "reason": "Atta, Cooking Oils & Rice bulk restocking", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "ind-sm-03", "indent_number": "IND-2026-00103", "requester_name": "Priya Menon", "department_id": "dept-03", "status": "Processing", "urgency": "High", "created_at": now_dt.strftime("%Y-%m-%d"), "total_value": 2800, "reason": "Soft drinks & Beverage chilled rack replenishment", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "ind-sm-04", "indent_number": "IND-2026-00104", "requester_name": "Rajesh Patel", "department_id": "dept-04", "status": "Under Review", "urgency": "Normal", "created_at": now_dt.strftime("%Y-%m-%d"), "total_value": 1900, "reason": "Dettol & Personal Care detergent replenishment", "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["indents"].extend(sm_indents)

    # 6. Supermarket POs (Pending POs)
    db["purchase_orders"] = [p for p in db.get("purchase_orders", []) if p.get("created_by") != DEMO_USER]
    sm_pos = [
        {"id": "po-sm-01", "po_number": "PO-2026-00301", "supplier_id": "sup-sm-01", "supplier_name": "GCMMF Amul Milk & Dairy Wholesale", "warehouse_id": "wh-01", "status": "Approved", "created_at": now_dt.strftime("%Y-%m-%d"), "delivery_date": (now_dt + timedelta(days=2)).strftime("%Y-%m-%d"), "total_amount": 5400, "tax_amount": 270, "grand_total": 5670, "items_count": 100, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "po-sm-02", "po_number": "PO-2026-00302", "supplier_id": "sup-sm-02", "supplier_name": "Nestlé India FMCG Distributors", "warehouse_id": "wh-01", "status": "Processing", "created_at": now_dt.strftime("%Y-%m-%d"), "delivery_date": (now_dt + timedelta(days=4)).strftime("%Y-%m-%d"), "total_amount": 8500, "tax_amount": 1530, "grand_total": 10030, "items_count": 250, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "po-sm-03", "po_number": "PO-2026-00303", "supplier_id": "sup-sm-03", "supplier_name": "Hindustan Unilever Wholesale Depot", "warehouse_id": "wh-02", "status": "Issued", "created_at": now_dt.strftime("%Y-%m-%d"), "delivery_date": (now_dt + timedelta(days=5)).strftime("%Y-%m-%d"), "total_amount": 6200, "tax_amount": 1116, "grand_total": 7316, "items_count": 180, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "po-sm-04", "po_number": "PO-2026-00304", "supplier_id": "sup-sm-05", "supplier_name": "ITC Agri & Staples Wholesale", "warehouse_id": "wh-01", "status": "Draft", "created_at": now_dt.strftime("%Y-%m-%d"), "delivery_date": (now_dt + timedelta(days=6)).strftime("%Y-%m-%d"), "total_amount": 9200, "tax_amount": 460, "grand_total": 9660, "items_count": 150, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["purchase_orders"].extend(sm_pos)

    # 7. Supermarket GRNs (Pending GRNs)
    db["goods_receipts"] = [g for g in db.get("goods_receipts", []) if g.get("created_by") != DEMO_USER]
    sm_grns = [
        {"id": "grn-sm-01", "grn_number": "GRN-2026-00401", "po_number": "PO-2026-00301", "supplier_name": "GCMMF Amul Milk & Dairy Wholesale", "warehouse_id": "wh-01", "status": "Under Quality Inspection", "received_date": now_dt.strftime("%Y-%m-%d"), "total_items": 4, "total_value": 5400, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "grn-sm-02", "grn_number": "GRN-2026-00402", "po_number": "PO-2026-00303", "supplier_name": "Hindustan Unilever Wholesale Depot", "warehouse_id": "wh-02", "status": "Pending Verification", "received_date": now_dt.strftime("%Y-%m-%d"), "total_items": 8, "total_value": 6200, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO},
        {"id": "grn-sm-03", "grn_number": "GRN-2026-00403", "po_number": "PO-2026-00304", "supplier_name": "Britannia Bakery Products Direct", "warehouse_id": "wh-01", "status": "Draft", "received_date": now_dt.strftime("%Y-%m-%d"), "total_items": 3, "total_value": 3100, "created_by": DEMO_USER, "company_name": DEMO_COMPANY, "is_demo": IS_DEMO}
    ]
    db["goods_receipts"].extend(sm_grns)

    # Save to PostgreSQL / JSON store
    save_db()

    print("=================================================================")
    print(f" SUCCESS! Created 50 Supermarket Items for {DEMO_USER}")
    print(f" EXACT TOTAL STOCK VALUE: INR {final_stock_val:,.2f}")
    print(f" Total Supermarket Items: {len([i for i in db['items'] if i.get('created_by') == DEMO_USER])}")
    print(f" Total Inventory Balances: {len([b for b in db['inventory_balances'] if b.get('created_by') == DEMO_USER])}")
    print(f" Total Ongoing Indents: {len(sm_indents)}")
    print(f" Total Pending POs: {len(sm_pos)}")
    print(f" Total Pending GRNs: {len(sm_grns)}")
    print("=================================================================")

if __name__ == "__main__":
    seed_supermarket_demo()
