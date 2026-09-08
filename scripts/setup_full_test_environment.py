import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from db.database_store import load_db, save_db, db

def setup_full_test_environment():
    print("\n========================================================")
    print("SETTING UP COMPLETE TEST ENVIRONMENT IN POSTGRESQL")
    print("========================================================\n")

    load_db()

    # 1. Setup Company Settings
    db["settings"] = {
        "company_name": "Enterprise Head Office",
        "company_address": "Corporate Tower, Tech Park, Kochi, Kerala - 682030",
        "company_email": "info@enterpriseheadoffice.com",
        "company_phone": "+91 484 2900000",
        "currency": "INR (₹)",
        "decimal_precision": 2,
        "fiscal_year_start": "01-04",
        "fiscal_year_end": "31-03"
    }

    # 2. Setup Departments (All 6 Required Departments)
    departments = [
        {"id": "dept-it", "name": "IT", "code": "IT-DEPT", "head_name": "Arun Department Manager", "budget_allocated": 1500000, "budget_used": 250000},
        {"id": "dept-stores", "name": "Stores", "code": "STORES-DEPT", "head_name": "Suresh Store Manager", "budget_allocated": 2000000, "budget_used": 410000},
        {"id": "dept-purchase", "name": "Purchase", "code": "PURCHASE-DEPT", "head_name": "Vishnu Purchase Manager", "budget_allocated": 3500000, "budget_used": 890000},
        {"id": "dept-finance", "name": "Finance", "code": "FINANCE-DEPT", "head_name": "Anjali Finance", "budget_allocated": 1000000, "budget_used": 180000},
        {"id": "dept-audit", "name": "Audit", "code": "AUDIT-DEPT", "head_name": "Audit User", "budget_allocated": 500000, "budget_used": 80000},
        {"id": "dept-mgmt", "name": "Management", "code": "MGMT-DEPT", "head_name": "Rajesh Director", "budget_allocated": 5000000, "budget_used": 1200000}
    ]
    
    existing_dept_map = {d.get("id"): d for d in db.get("departments", [])}
    for dept in departments:
        if dept["id"] in existing_dept_map:
            existing_dept_map[dept["id"]].update(dept)
        else:
            db.setdefault("departments", []).append(dept)

    # 3. Setup Warehouses & Bins
    warehouses = [
        {"id": "wh-ho-01", "name": "Central Head Office Warehouse", "code": "WH-HO-01", "city": "Kochi", "address": "Tech Zone 1, Kakkanad, Kochi", "is_active": True, "capacity_sqft": 50000},
        {"id": "wh-ho-02", "name": "Regional Logistics Hub", "code": "WH-REG-02", "city": "Bangalore", "address": "Industrial Layout, Whitefield, Bangalore", "is_active": True, "capacity_sqft": 35000}
    ]
    existing_wh_map = {w.get("id"): w for w in db.get("warehouses", [])}
    for wh in warehouses:
        if wh["id"] in existing_wh_map:
            existing_wh_map[wh["id"]].update(wh)
        else:
            db.setdefault("warehouses", []).append(wh)

    locations = [
        {"id": "loc-ho-101", "warehouse_id": "wh-ho-01", "bin_number": "A1-RACK-01", "zone": "Zone A (IT & Hardware)", "is_occupied": True},
        {"id": "loc-ho-102", "warehouse_id": "wh-ho-01", "bin_number": "A2-RACK-03", "zone": "Zone B (General Stores)", "is_occupied": True},
        {"id": "loc-ho-201", "warehouse_id": "wh-ho-02", "bin_number": "B1-RACK-02", "zone": "Zone C (Bulk Storage)", "is_occupied": True}
    ]
    existing_loc_map = {l.get("id"): l for l in db.get("locations", []) or db.get("warehouse_locations", [])}
    for loc in locations:
        if loc["id"] not in existing_loc_map:
            db.setdefault("warehouse_locations", []).append(loc)

    # 4. Setup Item Categories & Brands
    categories = [
        {"id": "cat-it-01", "name": "IT Hardware & Laptops", "code": "ELEC-IT", "description": "Laptops, Desktops, Scanners & Monitors"},
        {"id": "cat-office-02", "name": "Office Equipment & Printers", "code": "OFF-EQP", "description": "Printers, Cartridges, Ergonomic Chairs & Supplies"},
        {"id": "cat-raw-03", "name": "Consumables & Maintenance Tools", "code": "MAINT-TLS", "description": "Cleaning kits, cables, batteries & maintenance items"}
    ]
    existing_cat_map = {c.get("id"): c for c in db.get("item_categories", [])}
    for cat in categories:
        if cat["id"] in existing_cat_map:
            existing_cat_map[cat["id"]].update(cat)
        else:
            db.setdefault("item_categories", []).append(cat)

    brands = [
        {"id": "brd-dell", "name": "Dell Technologies", "code": "DELL"},
        {"id": "brd-hp", "name": "HP Enterprise", "code": "HP"},
        {"id": "brd-zebra", "name": "Zebra Technologies", "code": "ZEBRA"},
        {"id": "brd-logi", "name": "Logitech", "code": "LOGI"}
    ]
    existing_brd_map = {b.get("id"): b for b in db.get("brands", [])}
    for brd in brands:
        if brd["id"] in existing_brd_map:
            existing_brd_map[brd["id"]].update(brd)
        else:
            db.setdefault("brands", []).append(brd)

    # 5. Setup Item Master Catalog
    items = [
        {
            "id": "itm-lap-01",
            "item_code": "SKU-LAP-001",
            "item_name": "Dell Latitude 5440 Core i7 Laptop",
            "description": "14-inch FHD, 16GB RAM, 512GB SSD, Windows 11 Pro",
            "category_id": "cat-it-01",
            "brand_id": "brd-dell",
            "unit": "Pcs",
            "min_stock_level": 5,
            "max_stock_level": 50,
            "reorder_level": 8,
            "reorder_qty": 10,
            "valuation_rate": 65000.0,
            "current_stock": 15,
            "stock_value": 975000.0,
            "default_location_id": "loc-ho-101",
            "status": "In Stock"
        },
        {
            "id": "itm-lap-02",
            "item_code": "SKU-LAP-002",
            "item_name": "HP ProBook 450 G10 Laptop",
            "description": "15.6-inch FHD, Intel Core i5 13th Gen, 16GB RAM, 512GB SSD",
            "category_id": "cat-it-01",
            "brand_id": "brd-hp",
            "unit": "Pcs",
            "min_stock_level": 4,
            "max_stock_level": 40,
            "reorder_level": 6,
            "reorder_qty": 10,
            "valuation_rate": 58000.0,
            "current_stock": 12,
            "stock_value": 696000.0,
            "default_location_id": "loc-ho-101",
            "status": "In Stock"
        },
        {
            "id": "itm-scn-01",
            "item_code": "SKU-SCN-001",
            "item_name": "Zebra DS2208 Handheld Barcode Scanner",
            "description": "USB 1D/2D Imager Barcode Scanner with Stand",
            "category_id": "cat-it-01",
            "brand_id": "brd-zebra",
            "unit": "Pcs",
            "min_stock_level": 10,
            "max_stock_level": 60,
            "reorder_level": 15,
            "reorder_qty": 20,
            "valuation_rate": 8500.0,
            "current_stock": 25,
            "stock_value": 212500.0,
            "default_location_id": "loc-ho-101",
            "status": "In Stock"
        },
        {
            "id": "itm-prn-01",
            "item_code": "SKU-PRN-001",
            "item_name": "HP LaserJet Pro Printer M404dn",
            "description": "Monochrome Laser Printer, Auto Duplex, Ethernet",
            "category_id": "cat-office-02",
            "brand_id": "brd-hp",
            "unit": "Pcs",
            "min_stock_level": 3,
            "max_stock_level": 20,
            "reorder_level": 5,
            "reorder_qty": 5,
            "valuation_rate": 24000.0,
            "current_stock": 8,
            "stock_value": 192000.0,
            "default_location_id": "loc-ho-102",
            "status": "In Stock"
        },
        {
            "id": "itm-mon-01",
            "item_code": "SKU-MON-001",
            "item_name": "Dell 27-inch UltraSharp 4K Monitor",
            "description": "U2723QE IPS Black USB-C Hub Monitor",
            "category_id": "cat-it-01",
            "brand_id": "brd-dell",
            "unit": "Pcs",
            "min_stock_level": 5,
            "max_stock_level": 30,
            "reorder_level": 8,
            "reorder_qty": 10,
            "valuation_rate": 32000.0,
            "current_stock": 20,
            "stock_value": 640000.0,
            "default_location_id": "loc-ho-101",
            "status": "In Stock"
        }
    ]
    existing_item_map = {i.get("id"): i for i in db.get("items", [])}
    for item in items:
        if item["id"] in existing_item_map:
            existing_item_map[item["id"]].update(item)
        else:
            db.setdefault("items", []).append(item)

    # 6. Setup Suppliers Directory
    suppliers = [
        {
            "id": "sup-test-01",
            "supplier_code": "SUP-INF-01",
            "supplier_name": "Infotech Systems India Pvt Ltd",
            "contact_person": "Ramesh Kumar",
            "phone": "9895012345",
            "email": "sales@infotechsystems.in",
            "address_registered": "Infopark Campus, Kakkanad, Kochi, Kerala",
            "gst_number": "32AAAAA0000A1Z5",
            "payment_terms": "Net 30",
            "rating": 4.8
        },
        {
            "id": "sup-test-02",
            "supplier_code": "SUP-APX-02",
            "supplier_name": "Apex Office Solutions Kerala",
            "contact_person": "Sujith Nair",
            "phone": "9895067890",
            "email": "orders@apexoffice.com",
            "address_registered": "MG Road, Ernakulam, Kochi, Kerala",
            "gst_number": "32BBBBB1111B2Z8",
            "payment_terms": "Net 15",
            "rating": 4.6
        }
    ]
    existing_sup_map = {s.get("id"): s for s in db.get("suppliers", [])}
    for sup in suppliers:
        if sup["id"] in existing_sup_map:
            existing_sup_map[sup["id"]].update(sup)
        else:
            db.setdefault("suppliers", []).append(sup)

    # 7. Setup Ready-to-Test Material Indent (Created by Rahul Employee)
    sample_indents = [
        {
            "id": "ind-test-1001",
            "indent_number": "IND-2026-1001",
            "indent_date": "2026-09-05",
            "requested_by_id": "usr-test-02",
            "requested_by_name": "Rahul Employee",
            "requested_by_email": "inventory.test.employee@gmail.com",
            "department_id": "dept-it",
            "department_name": "IT",
            "purpose": "New Employee Laptop & Barcode Scanner Procurement for IT Dept",
            "priority": "High",
            "status": "Pending Department Approval",
            "approver_id": "usr-test-03",
            "approver_name": "Arun Department Manager",
            "items": [
                {"item_id": "itm-lap-01", "item_name": "Dell Latitude 5440 Core i7 Laptop", "qty": 5, "unit": "Pcs", "est_unit_rate": 65000, "total_est": 325000},
                {"item_id": "itm-scn-01", "item_name": "Zebra DS2208 Handheld Barcode Scanner", "qty": 5, "unit": "Pcs", "est_unit_rate": 8500, "total_est": 42500}
            ],
            "total_estimated_amount": 367500.0,
            "created_at": "2026-09-05T10:00:00"
        }
    ]
    existing_ind_map = {ind.get("id"): ind for ind in db.get("indents", [])}
    for ind in sample_indents:
        if ind["id"] in existing_ind_map:
            existing_ind_map[ind["id"]].update(ind)
        else:
            db.setdefault("indents", []).append(ind)

    # 8. Save all updated domains to PostgreSQL DB
    save_db("settings")
    save_db("departments")
    save_db("warehouses")
    save_db("warehouse_locations")
    save_db("item_categories")
    save_db("brands")
    save_db("items")
    save_db("suppliers")
    save_db("indents")

    print("[SUCCESS] All 6 Departments, Warehouses, Categories, Item Master Catalog, Suppliers & Sample Indent set up in PostgreSQL DB!")

if __name__ == "__main__":
    setup_full_test_environment()
