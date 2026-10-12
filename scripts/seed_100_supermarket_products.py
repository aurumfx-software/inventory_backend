import sys
import os
from datetime import datetime, timedelta

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from db.database_store import db, load_db, save_db

def seed_100_supermarket_products():
    print("==================================================================")
    print(" Populating 120+ Realistic Indian Supermarket Products...")
    print("==================================================================")

    load_db()

    DEMO_USER = "cashier@supermarket.com"
    DEMO_COMPANY = "Organization"
    IS_DEMO = True

    # 1. Supermarket Categories
    categories = [
        {"id": "cat-sm-01", "name": "Dairy & Bakery", "code": "DAIRY-BAKERY", "tax_rate_id": "tax-5", "description": "Milk, Butter, Cheese, Paneer, Curd & Fresh Bread"},
        {"id": "cat-sm-02", "name": "Snacks & Biscuits", "code": "SNACK-BISC", "tax_rate_id": "tax-12", "description": "Biscuits, Cookies, Chips, Namkeen & Chocolates"},
        {"id": "cat-sm-03", "name": "Beverages & Drinks", "code": "BEV-DRINK", "tax_rate_id": "tax-18", "description": "Teas, Coffees, Fruit Juices & Soft Drinks"},
        {"id": "cat-sm-04", "name": "Atta, Rice & Grains", "code": "ATTA-RICE", "tax_rate_id": "tax-5", "description": "Wheat Atta, Basmati Rice, Maida & Semolina"},
        {"id": "cat-sm-05", "name": "Dal, Pulses & Spices", "code": "DAL-SPICES", "tax_rate_id": "tax-5", "description": "Toor Dal, Moong, Chana, Masalas & Spices"},
        {"id": "cat-sm-06", "name": "Cooking Oils & Ghee", "code": "OIL-GHEE", "tax_rate_id": "tax-5", "description": "Sunflower Oil, Mustard Oil, Desi Cow Ghee"},
        {"id": "cat-sm-07", "name": "Personal Care & Hygiene", "code": "CARE-HYG", "tax_rate_id": "tax-18", "description": "Soaps, Shampoos, Toothpastes, Face Wash"},
        {"id": "cat-sm-08", "name": "Household & Cleaning", "code": "CLEAN-HOU", "tax_rate_id": "tax-18", "description": "Detergent Powders, Liquids, Floor & Toilet Cleaners"},
        {"id": "cat-sm-09", "name": "Baby Care", "code": "BABY-CARE", "tax_rate_id": "tax-12", "description": "Diapers, Baby Wipes & Infant Essentials"},
        {"id": "cat-sm-10", "name": "Stationery & Kitchen", "code": "STAT-KTCH", "tax_rate_id": "tax-12", "description": "Foil, Cling Wrap, Tissues, Kitchen Cleaners"},
        {"id": "cat-sm-11", "name": "Frozen Foods", "code": "FRZN-FOOD", "tax_rate_id": "tax-18", "description": "French Fries, Peas, Nuggets & Frozen Delights"},
    ]

    existing_cats = {c["id"]: c for c in db.get("item_categories", [])}
    for cat in categories:
        cat["created_by"] = DEMO_USER
        cat["company_name"] = DEMO_COMPANY
        cat["is_demo"] = IS_DEMO
        if cat["id"] in existing_cats:
            existing_cats[cat["id"]].update(cat)
        else:
            db["item_categories"].append(cat)

    # 2. Supermarket Brands
    brands = [
        {"id": "brd-sm-01", "name": "Amul", "code": "AMUL"},
        {"id": "brd-sm-02", "name": "Britannia", "code": "BRITAN"},
        {"id": "brd-sm-03", "name": "Nestlé", "code": "NESTLE"},
        {"id": "brd-sm-04", "name": "Hindustan Unilever", "code": "HUL"},
        {"id": "brd-sm-05", "name": "ITC Aashirvaad", "code": "ITC"},
        {"id": "brd-sm-06", "name": "Parle", "code": "PARLE"},
        {"id": "brd-sm-07", "name": "Fortune", "code": "FORTUNE"},
        {"id": "brd-sm-08", "name": "Coca-Cola / Pepsi", "code": "BEV-CORP"},
        {"id": "brd-sm-09", "name": "Dabur & Real", "code": "DABUR"},
        {"id": "brd-sm-10", "name": "Tata Sampann", "code": "TATA"},
        {"id": "brd-sm-11", "name": "Cadbury", "code": "CADBURY"},
        {"id": "brd-sm-12", "name": "Haldiram's", "code": "HALDIRAM"},
        {"id": "brd-sm-13", "name": "Colgate-Palmolive", "code": "COLGATE"},
        {"id": "brd-sm-14", "name": "Procter & Gamble", "code": "PG"},
        {"id": "brd-sm-15", "name": "Dettol (Reckitt)", "code": "DETTOL"},
        {"id": "brd-sm-16", "name": "Everest & MDH", "code": "SPICE-CORP"},
        {"id": "brd-sm-17", "name": "India Gate", "code": "KRBL"},
        {"id": "brd-sm-18", "name": "McCain", "code": "MCCAIN"},
        {"id": "brd-sm-19", "name": "Pampers", "code": "PAMPERS"},
        {"id": "brd-sm-20", "name": "Dhara / Saffola", "code": "MARICO"},
    ]

    existing_brds = {b["id"]: b for b in db.get("brands", [])}
    for brd in brands:
        brd["created_by"] = DEMO_USER
        brd["company_name"] = DEMO_COMPANY
        brd["is_demo"] = IS_DEMO
        if brd["id"] in existing_brds:
            existing_brds[brd["id"]].update(brd)
        else:
            db["brands"].append(brd)

    # 3. 120+ Products Definition
    # (name, cat_id, brd_id, uom_id, mrp, selling_price, cost_price, stock, min_stock, gst_rate, tax_rate_id, discount, offer)
    raw_products = [
        # --- 1. Atta, Rice & Grains (cat-sm-04) ---
        ("Aashirvaad Superior MP Chakki Atta 5kg", "cat-sm-04", "brd-sm-05", "uom-03", 320.0, 295.0, 260.0, 65, 10, 5.0, "tax-5", 7.81, "₹25 OFF"),
        ("India Gate Super Basmati Rice 5kg Bag", "cat-sm-04", "brd-sm-17", "uom-03", 650.0, 599.0, 510.0, 40, 8, 5.0, "tax-5", 7.85, "₹51 OFF"),
        ("Fortune Chakki Fresh Shuddh Atta 10kg", "cat-sm-04", "brd-sm-07", "uom-03", 480.0, 440.0, 390.0, 35, 10, 5.0, "tax-5", 8.33, "10% OFF"),
        ("Daawat Rozana Gold Basmati Rice 5kg", "cat-sm-04", "brd-sm-17", "uom-03", 495.0, 449.0, 380.0, 45, 8, 5.0, "tax-5", 9.29, "₹46 OFF"),
        ("Pillsbury Chakki Fresh Whole Wheat Atta 5kg", "cat-sm-04", "brd-sm-05", "uom-03", 310.0, 285.0, 245.0, 30, 6, 5.0, "tax-5", 8.06, "₹25 OFF"),
        ("India Gate Feast Rozzana Basmati Rice 1kg", "cat-sm-04", "brd-sm-17", "uom-03", 115.0, 99.0, 82.0, 80, 15, 5.0, "tax-5", 13.91, "15% OFF"),
        ("Aashirvaad Select Sharbati Wheat Atta 5kg", "cat-sm-04", "brd-sm-05", "uom-03", 360.0, 335.0, 290.0, 25, 5, 5.0, "tax-5", 6.94, "₹25 OFF"),
        ("Fortune Premium Quality Maida 1kg", "cat-sm-04", "brd-sm-07", "uom-03", 55.0, 48.0, 38.0, 60, 12, 5.0, "tax-5", 12.73, "10% OFF"),
        ("Tata Sampann Roasted Fine Sooji / Rawa 500g", "cat-sm-04", "brd-sm-10", "uom-01", 45.0, 39.0, 30.0, 50, 10, 5.0, "tax-5", 13.33, "₹6 OFF"),
        ("Rajdhani Poha Thick Poha 500g Pack", "cat-sm-04", "brd-sm-05", "uom-01", 50.0, 42.0, 32.0, 70, 15, 5.0, "tax-5", 16.0, "Buy 2 Get 1"),
        ("24 Mantra Organic Brown Rice 1kg Pack", "cat-sm-04", "brd-sm-10", "uom-03", 140.0, 125.0, 100.0, 35, 6, 5.0, "tax-5", 10.71, "10% OFF"),
        ("Fortune Besan Fine Chickpea Flour 500g", "cat-sm-04", "brd-sm-07", "uom-01", 65.0, 58.0, 46.0, 55, 10, 5.0, "tax-5", 10.77, "₹7 OFF"),

        # --- 2. Dal, Pulses & Spices (cat-sm-05) ---
        ("Tata Sampann Unpolished Toor Dal 1kg", "cat-sm-05", "brd-sm-10", "uom-03", 195.0, 175.0, 150.0, 50, 10, 5.0, "tax-5", 10.26, "10% OFF"),
        ("Tata Sampann Yellow Moong Dal Split 1kg", "cat-sm-05", "brd-sm-10", "uom-03", 165.0, 149.0, 125.0, 45, 10, 5.0, "tax-5", 9.70, "₹16 OFF"),
        ("Tata Sampann Premium Chana Dal 1kg", "cat-sm-05", "brd-sm-10", "uom-03", 120.0, 105.0, 88.0, 60, 12, 5.0, "tax-5", 12.50, "₹15 OFF"),
        ("Tata Sampann Masoor Malka Dal 1kg Pack", "cat-sm-05", "brd-sm-10", "uom-03", 130.0, 115.0, 95.0, 40, 8, 5.0, "tax-5", 11.54, "10% OFF"),
        ("Everest Royal Garam Masala Powder 100g", "cat-sm-05", "brd-sm-16", "uom-01", 85.0, 76.0, 60.0, 75, 15, 5.0, "tax-5", 10.59, "10% OFF"),
        ("MDH Kashmiri Deggi Mirch Powder 100g", "cat-sm-05", "brd-sm-16", "uom-01", 100.0, 89.0, 70.0, 80, 15, 5.0, "tax-5", 11.0, "₹11 OFF"),
        ("Catch Super Turmeric / Haldi Powder 200g", "cat-sm-05", "brd-sm-16", "uom-01", 72.0, 62.0, 48.0, 90, 20, 5.0, "tax-5", 13.89, "₹10 OFF"),
        ("Everest Coriander / Dhaniya Powder 200g", "cat-sm-05", "brd-sm-16", "uom-01", 75.0, 66.0, 52.0, 65, 12, 5.0, "tax-5", 12.0, "Buy 2 Get 1"),
        ("Tata Salt Vacuum Evaporated Iodised 1kg", "cat-sm-05", "brd-sm-10", "uom-01", 28.0, 25.0, 20.0, 120, 25, 0.0, "tax-0", 10.71, "None"),
        ("Madhur Pure & Hygienic Refined Sugar 1kg", "cat-sm-05", "brd-sm-05", "uom-01", 62.0, 54.0, 44.0, 100, 20, 5.0, "tax-5", 12.90, "₹8 OFF"),
        ("Everest Sambhar Masala Powder 100g Pack", "cat-sm-05", "brd-sm-16", "uom-01", 68.0, 59.0, 46.0, 55, 10, 5.0, "tax-5", 13.24, "₹9 OFF"),
        ("MDH Kitchen King All-Rounder Masala 100g", "cat-sm-05", "brd-sm-16", "uom-01", 90.0, 80.0, 62.0, 60, 12, 5.0, "tax-5", 11.11, "10% OFF"),

        # --- 3. Cooking Oils & Ghee (cat-sm-06) ---
        ("Fortune Sunlite Refined Sunflower Oil 1L Pouch", "cat-sm-06", "brd-sm-07", "uom-05", 155.0, 139.0, 118.0, 85, 15, 5.0, "tax-5", 10.32, "₹16 OFF"),
        ("Saffola Gold Pro Healthy Blend Oil 1L Pouch", "cat-sm-06", "brd-sm-20", "uom-05", 195.0, 175.0, 148.0, 50, 10, 5.0, "tax-5", 10.26, "10% OFF"),
        ("Amul Pure Ghee 1L Tin / Pack", "cat-sm-06", "brd-sm-01", "uom-05", 640.0, 595.0, 520.0, 40, 8, 5.0, "tax-5", 7.03, "₹45 OFF"),
        ("Fortune Kachi Ghani Mustard Oil 1L PET Bottle", "cat-sm-06", "brd-sm-07", "uom-05", 170.0, 152.0, 128.0, 65, 12, 5.0, "tax-5", 10.59, "10% OFF"),
        ("Dhara Refined Groundnut Peanut Oil 1L", "cat-sm-06", "brd-sm-20", "uom-05", 210.0, 189.0, 160.0, 35, 6, 5.0, "tax-5", 10.0, "₹21 OFF"),
        ("Patanjali Pure Cow Ghee 500ml Carton", "cat-sm-06", "brd-sm-01", "uom-01", 330.0, 299.0, 255.0, 45, 8, 5.0, "tax-5", 9.39, "₹31 OFF"),
        ("Borges Extra Virgin Olive Oil 500ml Glass", "cat-sm-06", "brd-sm-07", "uom-01", 750.0, 675.0, 560.0, 20, 4, 5.0, "tax-5", 10.0, "10% OFF"),

        # --- 4. Dairy & Bakery (cat-sm-01) ---
        ("Amul Taaza Homogenised Toned Milk 1L Tetra", "cat-sm-01", "brd-sm-01", "uom-05", 74.0, 69.0, 58.0, 60, 15, 5.0, "tax-5", 6.76, "₹5 OFF"),
        ("Amul Pasteurised Salted Butter 500g Brick", "cat-sm-01", "brd-sm-01", "uom-01", 285.0, 269.0, 235.0, 40, 10, 5.0, "tax-5", 5.61, "₹16 OFF"),
        ("Amul Malai Fresh Paneer Block 200g", "cat-sm-01", "brd-sm-01", "uom-01", 95.0, 88.0, 74.0, 45, 10, 5.0, "tax-5", 7.37, "₹7 OFF"),
        ("Britannia 100% Whole Wheat Brown Bread 400g", "cat-sm-01", "brd-sm-02", "uom-01", 50.0, 45.0, 36.0, 50, 12, 5.0, "tax-5", 10.0, "10% OFF"),
        ("Mother Dairy Classic Curd / Dahi 400g Cup", "cat-sm-01", "brd-sm-01", "uom-01", 50.0, 45.0, 36.0, 40, 10, 5.0, "tax-5", 10.0, "₹5 OFF"),
        ("Amul Processed Cheese Block 200g Pack", "cat-sm-01", "brd-sm-01", "uom-01", 145.0, 132.0, 110.0, 35, 8, 5.0, "tax-5", 8.97, "₹13 OFF"),
        ("Britannia Milk Bread Classic Sliced 400g", "cat-sm-01", "brd-sm-02", "uom-01", 45.0, 40.0, 32.0, 55, 12, 5.0, "tax-5", 11.11, "₹5 OFF"),
        ("Farm Fresh Table Eggs Carton (Pack of 6)", "cat-sm-01", "brd-sm-01", "uom-01", 54.0, 48.0, 38.0, 80, 20, 0.0, "tax-0", 11.11, "Buy 2 Get 1"),
        ("Amul Masti Spiced Buttermilk 200ml Tetra", "cat-sm-01", "brd-sm-01", "uom-01", 15.0, 15.0, 11.0, 90, 20, 5.0, "tax-5", 0.0, "None"),
        ("Nestlé Everyday Dairy Whitener Milk Powder 400g", "cat-sm-01", "brd-sm-03", "uom-01", 240.0, 219.0, 185.0, 30, 6, 5.0, "tax-5", 8.75, "₹21 OFF"),
        ("Amul Fresh Cream Low Fat 250ml Tetra Pack", "cat-sm-01", "brd-sm-01", "uom-01", 70.0, 65.0, 52.0, 40, 8, 5.0, "tax-5", 7.14, "₹5 OFF"),

        # --- 5. Snacks, Biscuits & Chocolates (cat-sm-02) ---
        ("Britannia Good Day Cashew Delight Cookies 200g", "cat-sm-02", "brd-sm-02", "uom-01", 50.0, 42.0, 32.0, 100, 20, 12.0, "tax-12", 16.0, "Buy 2 Get 1"),
        ("Parle-G Original Glucose Biscuits 250g Pack", "cat-sm-02", "brd-sm-06", "uom-01", 30.0, 27.0, 21.0, 150, 30, 12.0, "tax-12", 10.0, "10% OFF"),
        ("Sunfeast Dark Fantasy Choco Fills 300g Big Pack", "cat-sm-02", "brd-sm-05", "uom-01", 160.0, 135.0, 105.0, 45, 10, 12.0, "tax-12", 15.63, "15% OFF"),
        ("Oreo Original Vanilla Creme Sandwich Biscuits 120g", "cat-sm-02", "brd-sm-11", "uom-01", 40.0, 35.0, 26.0, 80, 15, 12.0, "tax-12", 12.50, "₹5 OFF"),
        ("Cadbury Dairy Milk Silk Chocolate Bar 150g", "cat-sm-02", "brd-sm-11", "uom-01", 185.0, 165.0, 135.0, 60, 12, 18.0, "tax-18", 10.81, "₹20 OFF"),
        ("Nestlé KitKat 4-Finger Crisp Wafer Bar 38.5g", "cat-sm-02", "brd-sm-03", "uom-01", 35.0, 30.0, 22.0, 120, 25, 18.0, "tax-18", 14.29, "Buy 3 Get 1"),
        ("Lay's India's Magic Masala Potato Chips 50g", "cat-sm-02", "brd-sm-08", "uom-01", 20.0, 18.0, 13.0, 140, 30, 12.0, "tax-12", 10.0, "10% OFF"),
        ("Kurkure Masala Munch Crunchy Snacks 90g", "cat-sm-02", "brd-sm-08", "uom-01", 20.0, 18.0, 13.0, 130, 25, 12.0, "tax-12", 10.0, "10% OFF"),
        ("Haldiram's Nagpur Aloo Bhujia Namkeen 200g", "cat-sm-02", "brd-sm-12", "uom-01", 60.0, 52.0, 40.0, 85, 15, 12.0, "tax-12", 13.33, "₹8 OFF"),
        ("Haldiram's Nagpur Khatta Meetha Mixture 200g", "cat-sm-02", "brd-sm-12", "uom-01", 60.0, 52.0, 40.0, 75, 15, 12.0, "tax-12", 13.33, "Buy 2 Get 1"),
        ("Maggi 2-Minute Masala Instant Noodles 4-Pack", "cat-sm-02", "brd-sm-03", "uom-01", 60.0, 54.0, 42.0, 110, 20, 12.0, "tax-12", 10.0, "10% OFF"),
        ("Yippee Mood Masala Magic Instant Noodles 260g", "cat-sm-02", "brd-sm-05", "uom-01", 55.0, 48.0, 38.0, 70, 12, 12.0, "tax-12", 12.73, "₹7 OFF"),
        ("Doritos Cheese Supreme Nacho Chips 60g", "cat-sm-02", "brd-sm-08", "uom-01", 30.0, 27.0, 20.0, 65, 12, 12.0, "tax-12", 10.0, "10% OFF"),
        ("Cadbury Celebrations Rich Dry Fruit Gift Box 177g", "cat-sm-02", "brd-sm-11", "uom-01", 350.0, 299.0, 240.0, 30, 5, 18.0, "tax-18", 14.57, "₹51 OFF"),
        ("Pringles Original Potato Crisps Canister 107g", "cat-sm-02", "brd-sm-08", "uom-01", 125.0, 110.0, 88.0, 40, 8, 12.0, "tax-12", 12.0, "10% OFF"),

        # --- 6. Beverages & Drinks (cat-sm-03) ---
        ("Taj Mahal Long Leaf Premium Tea 500g Carton", "cat-sm-03", "brd-sm-04", "uom-01", 380.0, 339.0, 280.0, 50, 10, 5.0, "tax-5", 10.79, "₹41 OFF"),
        ("Red Label Strong Blend CTC Tea 1kg Poly", "cat-sm-03", "brd-sm-04", "uom-01", 540.0, 485.0, 410.0, 45, 8, 5.0, "tax-5", 10.19, "10% OFF"),
        ("Tata Tea Gold Rich Taste & Aroma 500g", "cat-sm-03", "brd-sm-10", "uom-01", 320.0, 289.0, 240.0, 55, 10, 5.0, "tax-5", 9.69, "₹31 OFF"),
        ("Nescafé Classic 100% Pure Instant Coffee 100g Jar", "cat-sm-03", "brd-sm-03", "uom-01", 340.0, 305.0, 250.0, 50, 10, 18.0, "tax-18", 10.29, "₹35 OFF"),
        ("Bru Instant Roasted Coffee-Chicory 100g Jar", "cat-sm-03", "brd-sm-04", "uom-01", 230.0, 205.0, 168.0, 60, 12, 18.0, "tax-18", 10.87, "10% OFF"),
        ("Real Fruit Power 100% Mixed Fruit Juice 1L Tetra", "cat-sm-03", "brd-sm-09", "uom-05", 130.0, 115.0, 92.0, 75, 15, 12.0, "tax-12", 11.54, "10% OFF"),
        ("Tropicana 100% Orange Fruit Juice 1L Tetra", "cat-sm-03", "brd-sm-08", "uom-05", 140.0, 122.0, 98.0, 65, 12, 12.0, "tax-12", 12.86, "₹18 OFF"),
        ("Coca-Cola Refreshing Soft Drink 750ml PET Bottle", "cat-sm-03", "brd-sm-08", "uom-01", 40.0, 38.0, 28.0, 100, 25, 28.0, "tax-28", 5.0, "Buy 3 Get 1"),
        ("Thums Up Charged Carbonated Beverage 750ml", "cat-sm-03", "brd-sm-08", "uom-01", 40.0, 38.0, 28.0, 110, 25, 28.0, "tax-28", 5.0, "Buy 3 Get 1"),
        ("Sprite Lemon-Lime Soft Drink 750ml PET", "cat-sm-03", "brd-sm-08", "uom-01", 40.0, 38.0, 28.0, 95, 20, 28.0, "tax-28", 5.0, "Buy 3 Get 1"),
        ("Red Bull Original Energy Drink Can 250ml", "cat-sm-03", "brd-sm-08", "uom-01", 125.0, 115.0, 94.0, 70, 15, 28.0, "tax-28", 8.0, "10% OFF"),
        ("Paper Boat Aamras Mango Juice Pouch 250ml", "cat-sm-03", "brd-sm-09", "uom-01", 35.0, 32.0, 24.0, 85, 20, 12.0, "tax-12", 8.57, "Buy 2 Get 1"),
        ("Bournvita Chocolate Nutrition Health Drink 500g Jar", "cat-sm-03", "brd-sm-11", "uom-01", 245.0, 225.0, 185.0, 45, 8, 18.0, "tax-18", 8.16, "₹20 OFF"),
        ("Horlicks Classic Malt Health Nutrition Drink 500g", "cat-sm-03", "brd-sm-04", "uom-01", 260.0, 238.0, 195.0, 40, 8, 18.0, "tax-18", 8.46, "₹22 OFF"),

        # --- 7. Personal Care & Hygiene (cat-sm-07) ---
        ("Dettol Original Germ Protection Soap 125g (Buy 3 Get 1)", "cat-sm-07", "brd-sm-15", "uom-01", 175.0, 155.0, 125.0, 80, 15, 18.0, "tax-18", 11.43, "₹20 OFF"),
        ("Dove Deep Moisture Bathing Beauty Bar 100g (Pack of 3)", "cat-sm-07", "brd-sm-04", "uom-01", 240.0, 210.0, 168.0, 60, 12, 18.0, "tax-18", 12.50, "15% OFF"),
        ("Colgate Strong Teeth Dental Toothpaste 300g Saver Pack", "cat-sm-07", "brd-sm-13", "uom-01", 185.0, 162.0, 130.0, 95, 20, 18.0, "tax-18", 12.43, "₹23 OFF"),
        ("Sensodyne Fresh Mint Sensitive Toothpaste 100g", "cat-sm-07", "brd-sm-13", "uom-01", 210.0, 189.0, 150.0, 50, 10, 18.0, "tax-18", 10.0, "10% OFF"),
        ("Head & Shoulders Anti-Dandruff Cool Menthol Shampoo 340ml", "cat-sm-07", "brd-sm-14", "uom-01", 360.0, 319.0, 255.0, 45, 8, 18.0, "tax-18", 11.39, "₹41 OFF"),
        ("Dove Intense Repair Hair Shampoo 340ml Pump Bottle", "cat-sm-07", "brd-sm-04", "uom-01", 380.0, 335.0, 270.0, 40, 8, 18.0, "tax-18", 11.84, "₹45 OFF"),
        ("Dettol Liquid Handwash Refill Pouch 675ml Saver", "cat-sm-07", "brd-sm-15", "uom-01", 119.0, 105.0, 82.0, 75, 15, 18.0, "tax-18", 11.76, "10% OFF"),
        ("Lifebuoy Total Germ Protection Handwash 750ml Refill", "cat-sm-07", "brd-sm-04", "uom-01", 115.0, 99.0, 78.0, 80, 15, 18.0, "tax-18", 13.91, "₹16 OFF"),
        ("Nivea Soft Light Moisturizing Cream 200ml Tub", "cat-sm-07", "brd-sm-04", "uom-01", 299.0, 259.0, 205.0, 40, 8, 18.0, "tax-18", 13.38, "₹40 OFF"),
        ("Vaseline Deep Moisture Body Lotion 400ml Pump", "cat-sm-07", "brd-sm-04", "uom-01", 375.0, 325.0, 260.0, 35, 6, 18.0, "tax-18", 13.33, "15% OFF"),
        ("Gillette Mach3 Men Shaving Razor Blades (Pack of 4)", "cat-sm-07", "brd-sm-14", "uom-01", 580.0, 520.0, 420.0, 30, 5, 18.0, "tax-18", 10.34, "₹60 OFF"),
        ("Colgate Super Flexi Medium Toothbrush (Buy 2 Get 1 Free)", "cat-sm-07", "brd-sm-13", "uom-01", 60.0, 50.0, 38.0, 100, 20, 18.0, "tax-18", 16.67, "Buy 2 Get 1"),
        ("Oral-B Pro-Health Soft Bristle Toothbrush", "cat-sm-07", "brd-sm-14", "uom-01", 45.0, 39.0, 28.0, 90, 15, 18.0, "tax-18", 13.33, "10% OFF"),
        ("Whisper Choice Ultra XL Sanitary Pads Wings (Pack of 20)", "cat-sm-07", "brd-sm-14", "uom-01", 160.0, 139.0, 110.0, 60, 12, 12.0, "tax-12", 13.13, "₹21 OFF"),
        ("Stayfree Secure Cottony Soft Wings Sanitary Pads (28s)", "cat-sm-07", "brd-sm-04", "uom-01", 195.0, 172.0, 138.0, 55, 10, 12.0, "tax-12", 11.79, "10% OFF"),
        ("Parachute 100% Pure Coconut Hair Oil 500ml Bottle", "cat-sm-07", "brd-sm-20", "uom-01", 215.0, 192.0, 155.0, 70, 15, 5.0, "tax-5", 10.70, "₹23 OFF"),
        ("Bajaj Almond Drops Non-Sticky Hair Oil 300ml Glass", "cat-sm-07", "brd-sm-20", "uom-01", 230.0, 205.0, 165.0, 50, 10, 18.0, "tax-18", 10.87, "10% OFF"),

        # --- 8. Household & Cleaning (cat-sm-08) ---
        ("Surf Excel Matic Front Load Detergent Powder 2kg Box", "cat-sm-08", "brd-sm-04", "uom-01", 450.0, 399.0, 320.0, 60, 12, 18.0, "tax-18", 11.33, "₹51 OFF"),
        ("Surf Excel Easy Wash Detergent Powder 1kg Poly", "cat-sm-08", "brd-sm-04", "uom-03", 145.0, 132.0, 105.0, 80, 15, 18.0, "tax-18", 8.97, "₹13 OFF"),
        ("Ariel Matic Top Load Washing Powder 2kg Saver Pack", "cat-sm-08", "brd-sm-14", "uom-01", 460.0, 409.0, 328.0, 50, 10, 18.0, "tax-18", 11.09, "₹51 OFF"),
        ("Tide Plus Extra Power Detergent Powder Jasmine 2kg", "cat-sm-08", "brd-sm-14", "uom-01", 280.0, 249.0, 198.0, 70, 12, 18.0, "tax-18", 11.07, "₹31 OFF"),
        ("Rin Advanced Detergent Bar 250g (Pack of 4)", "cat-sm-08", "brd-sm-04", "uom-01", 80.0, 72.0, 56.0, 90, 20, 18.0, "tax-18", 10.0, "10% OFF"),
        ("Vim Lemon Dishwash Gel Super Saver Pouch 750ml", "cat-sm-08", "brd-sm-04", "uom-01", 165.0, 145.0, 115.0, 85, 15, 18.0, "tax-18", 12.12, "₹20 OFF"),
        ("Vim Dishwash Bar with Polycoat 300g (Buy 3 Get 1)", "cat-sm-08", "brd-sm-04", "uom-01", 65.0, 55.0, 42.0, 110, 20, 18.0, "tax-18", 15.38, "Buy 3 Get 1"),
        ("Pril Lime Concentrated Dishwash Liquid 425ml", "cat-sm-08", "brd-sm-04", "uom-01", 120.0, 106.0, 84.0, 60, 12, 18.0, "tax-18", 11.67, "10% OFF"),
        ("Harpic Power Plus 10X Toilet Cleaner Original 1L", "cat-sm-08", "brd-sm-15", "uom-01", 215.0, 189.0, 150.0, 80, 15, 18.0, "tax-18", 12.09, "₹26 OFF"),
        ("Lizol Disinfectant Surface Floor Cleaner Citrus 1L", "cat-sm-08", "brd-sm-15", "uom-01", 225.0, 199.0, 158.0, 75, 15, 18.0, "tax-18", 11.56, "₹26 OFF"),
        ("Colin Advanced Glass & Surface Cleaner Spray 500ml", "cat-sm-08", "brd-sm-15", "uom-01", 110.0, 98.0, 76.0, 65, 12, 18.0, "tax-18", 10.91, "10% OFF"),
        ("Comfort After Wash Morning Fresh Fabric Conditioner 860ml", "cat-sm-08", "brd-sm-04", "uom-01", 235.0, 205.0, 162.0, 45, 8, 18.0, "tax-18", 12.77, "₹30 OFF"),
        ("Good Knight Gold Flash Liquid Mosquito Refill (Twin Pack)", "cat-sm-08", "brd-sm-15", "uom-01", 155.0, 138.0, 108.0, 70, 15, 18.0, "tax-18", 10.97, "₹17 OFF"),
        ("Odonil Room Air Freshener Blocks 50g (Pack of 4)", "cat-sm-08", "brd-sm-09", "uom-01", 190.0, 165.0, 128.0, 50, 10, 18.0, "tax-18", 13.16, "₹25 OFF"),

        # --- 9. Baby Care (cat-sm-09) ---
        ("Pampers All Round Protection Baby Diaper Pants L (44s)", "cat-sm-09", "brd-sm-19", "uom-01", 899.0, 799.0, 640.0, 35, 6, 12.0, "tax-12", 11.12, "₹100 OFF"),
        ("Pampers Baby Diaper Pants Medium M (52 Count)", "cat-sm-09", "brd-sm-19", "uom-01", 949.0, 849.0, 680.0, 30, 5, 12.0, "tax-12", 10.54, "₹100 OFF"),
        ("Huggies Wonder Pants Baby Diapers Large (36s)", "cat-sm-09", "brd-sm-19", "uom-01", 699.0, 619.0, 495.0, 40, 8, 12.0, "tax-12", 11.44, "₹80 OFF"),
        ("Johnson's Baby Gentle Cleansing Wipes (72 Wipes)", "cat-sm-09", "brd-sm-04", "uom-01", 220.0, 189.0, 148.0, 55, 10, 18.0, "tax-18", 14.09, "Buy 2 Get 1"),
        ("Johnson's Baby Soft Delicate Powder 400g", "cat-sm-09", "brd-sm-04", "uom-01", 270.0, 239.0, 190.0, 40, 8, 18.0, "tax-18", 11.48, "₹31 OFF"),
        ("Himalaya Gentle Baby Shampoo 200ml Bottle", "cat-sm-09", "brd-sm-04", "uom-01", 195.0, 172.0, 135.0, 45, 8, 18.0, "tax-18", 11.79, "10% OFF"),
        ("Cerelac Wheat-Apple Baby Cereal Stage 1 300g", "cat-sm-09", "brd-sm-03", "uom-01", 295.0, 275.0, 230.0, 35, 6, 5.0, "tax-5", 6.78, "₹20 OFF"),

        # --- 10. Stationery & Kitchen Essentials (cat-sm-10) ---
        ("Freshwrapp Aluminum Foil Roll 9 Meters Food Grade", "cat-sm-10", "brd-sm-05", "uom-01", 125.0, 109.0, 85.0, 60, 12, 18.0, "tax-18", 12.80, "₹16 OFF"),
        ("Origami So Soft 2-Ply Facial Tissues (Pack of 100)", "cat-sm-10", "brd-sm-05", "uom-01", 85.0, 72.0, 54.0, 75, 15, 12.0, "tax-12", 15.29, "Buy 2 Get 1"),
        ("Classmate Long Exercise Notebook 172 Pages Ruled", "cat-sm-10", "brd-sm-05", "uom-01", 65.0, 55.0, 42.0, 90, 20, 12.0, "tax-12", 15.38, "15% OFF"),
        ("Reynolds 045 Fine Carbide Ball Pens (Pack of 5)", "cat-sm-10", "brd-sm-05", "uom-01", 50.0, 42.0, 30.0, 120, 25, 12.0, "tax-12", 16.0, "Buy 2 Get 1"),
        ("Scotch-Brite Heavy Duty Scrub Pad (Pack of 3)", "cat-sm-10", "brd-sm-04", "uom-01", 60.0, 52.0, 38.0, 100, 20, 18.0, "tax-18", 13.33, "Buy 3 Get 1"),
        ("Cleanwrap Cling Film Food Wrap Roll 30 Meters", "cat-sm-10", "brd-sm-05", "uom-01", 160.0, 139.0, 108.0, 45, 8, 18.0, "tax-18", 13.13, "₹21 OFF"),
        ("Shalimar Garbage Trash Bags Medium (Pack of 30)", "cat-sm-10", "brd-sm-05", "uom-01", 110.0, 95.0, 72.0, 70, 12, 18.0, "tax-18", 13.64, "₹15 OFF"),

        # --- 11. Frozen Foods (cat-sm-11) ---
        ("McCain French Fries Crispy 420g Frozen Pack", "cat-sm-11", "brd-sm-18", "uom-01", 125.0, 110.0, 86.0, 45, 10, 18.0, "tax-18", 12.0, "10% OFF"),
        ("McCain Smiles Mashed Potato Shapes 415g", "cat-sm-11", "brd-sm-18", "uom-01", 135.0, 119.0, 92.0, 40, 8, 18.0, "tax-18", 11.85, "₹16 OFF"),
        ("Safal Select Frozen Green Peas 1kg Pouch", "cat-sm-11", "brd-sm-01", "uom-01", 160.0, 139.0, 110.0, 50, 10, 5.0, "tax-5", 13.13, "₹21 OFF"),
        ("Kwality Wall's Rich Chocolate Brownie Ice Cream 700ml", "cat-sm-11", "brd-sm-04", "uom-01", 240.0, 210.0, 165.0, 35, 6, 18.0, "tax-18", 12.50, "₹30 OFF"),
        ("Amul Real Milk Vanilla Magic Ice Cream Tub 1L", "cat-sm-11", "brd-sm-01", "uom-01", 190.0, 169.0, 135.0, 40, 8, 18.0, "tax-18", 11.05, "₹21 OFF"),
        ("ID Fresh Ready Wheat Malabar Parota (Pack of 5)", "cat-sm-11", "brd-sm-05", "uom-01", 95.0, 85.0, 66.0, 50, 10, 5.0, "tax-5", 10.53, "₹10 OFF"),
        ("Sumeru Frozen Crispy Chicken Popcorn 250g", "cat-sm-11", "brd-sm-18", "uom-01", 195.0, 172.0, 135.0, 30, 5, 18.0, "tax-18", 11.79, "10% OFF"),
        ("McCain Veggie Burger Patty (Pack of 4)", "cat-sm-11", "brd-sm-18", "uom-01", 140.0, 122.0, 95.0, 35, 6, 18.0, "tax-18", 12.86, "₹18 OFF"),
    ]

    print(f"Total raw products listed: {len(raw_products)}")

    # 4. Remove existing demo products that have SKU prefix or old SM- prefix
    existing_items = db.get("items", [])
    # Keep only non-supermarket items if any, or cleanly wipe items with SKU / SM codes
    cleaned_items = [i for i in existing_items if not (i.get("item_code", "").startswith("SKU") or i.get("item_code", "").startswith("SM-"))]

    existing_balances = db.get("inventory_balances", [])
    cleaned_balances = [b for b in existing_balances if not (b.get("item_code", "").startswith("SKU") or b.get("item_code", "").startswith("SM-"))]

    db["items"] = cleaned_items
    db["inventory_balances"] = cleaned_balances

    now_dt = datetime.now()

    # Generate sequential SKU000001, SKU000002... and 890100000001, 890100000002...
    for idx, p in enumerate(raw_products):
        seq = idx + 1
        sku = f"SKU{seq:06d}"
        barcode = f"89010000{seq:04d}"
        item_id = f"itm-sku-{seq:06d}"

        name, cat_id, brd_id, uom_id, mrp, selling_price, cost_price, stock, min_stock, gst_rate, tax_rate_id, disc, offer = p

        # Resolve category name & brand name
        cat_obj = next((c for c in db.get("item_categories", []) if c["id"] == cat_id), {})
        brd_obj = next((b for b in db.get("brands", []) if b["id"] == brd_id), {})

        item_obj = {
            "id": item_id,
            "item_code": sku,
            "sku": sku,
            "barcode": barcode,
            "name": name,
            "category_id": cat_id,
            "category_name": cat_obj.get("name", "Grocery"),
            "brand_id": brd_id,
            "brand_name": brd_obj.get("name", "General"),
            "uom_id": uom_id,
            "unit_price": selling_price,
            "mrp": mrp,
            "cost_price": cost_price,
            "valuation_rate": cost_price,
            "reorder_level": min_stock * 2,
            "min_stock": min_stock,
            "max_stock": stock * 3,
            "available_qty": stock,
            "on_hand_qty": stock,
            "gst_rate": gst_rate,
            "tax_rate_id": tax_rate_id,
            "discount": disc,
            "offer": offer,
            "status": "Active",
            "description": f"Supermarket SKU {sku} - {name} ({cat_obj.get('name')})",
            "created_by": DEMO_USER,
            "company_name": DEMO_COMPANY,
            "is_demo": IS_DEMO,
            "created_at": now_dt.isoformat()
        }
        db["items"].append(item_obj)

        bal_id = f"bal-sku-{seq:06d}"
        balance_obj = {
            "id": bal_id,
            "item_id": item_id,
            "item_code": sku,
            "item_name": name,
            "warehouse_id": "wh-01",
            "location_id": "loc-101",
            "quantity": stock,
            "on_hand_qty": stock,
            "reserved_qty": 0,
            "available_qty": stock,
            "batch_number": f"BAT-2026-{seq:04d}",
            "unit_cost": cost_price,
            "created_by": DEMO_USER,
            "company_name": DEMO_COMPANY,
            "is_demo": IS_DEMO,
            "created_at": now_dt.isoformat()
        }
        db["inventory_balances"].append(balance_obj)

    print(f"Successfully added {len(raw_products)} supermarket items into db dict.")
    print("Saving to PostgreSQL database...")
    save_db("item_categories")
    save_db("brands")
    save_db("items")
    save_db("inventory_balances")
    print("==================================================================")
    print(f" Database successfully seeded with {len(raw_products)} Products!")
    print(f" First Product: {raw_products[0][0]} | SKU000001 | 890100000001")
    print(f" Last Product: {raw_products[-1][0]} | SKU{len(raw_products):06d} | 89010000{len(raw_products):04d}")
    print("==================================================================")

if __name__ == "__main__":
    seed_100_supermarket_products()
