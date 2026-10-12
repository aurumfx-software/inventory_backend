import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import engine
from sqlalchemy import text

print("Starting billing tables migration...")

with engine.begin() as conn:
    # 1. billing_customers
    conn.execute(text("""
        ALTER TABLE billing_customers ADD COLUMN IF NOT EXISTS name VARCHAR(150);
        ALTER TABLE billing_customers ADD COLUMN IF NOT EXISTS phone VARCHAR(50);
        ALTER TABLE billing_customers ADD COLUMN IF NOT EXISTS email VARCHAR(150);
        ALTER TABLE billing_customers ADD COLUMN IF NOT EXISTS address VARCHAR(300);
        ALTER TABLE billing_customers ADD COLUMN IF NOT EXISTS created_at VARCHAR(50);
    """))
    conn.execute(text("""
        UPDATE billing_customers SET
            name = COALESCE(payload->>'name', ''),
            phone = COALESCE(payload->>'phone', ''),
            email = COALESCE(payload->>'email', ''),
            address = COALESCE(payload->>'address', ''),
            created_at = COALESCE(payload->>'created_at', '')
        WHERE payload IS NOT NULL;
    """))
    print("billing_customers columns added and backfilled.")
    
    # 2. invoices
    conn.execute(text("""
        ALTER TABLE invoices ADD COLUMN IF NOT EXISTS invoice_number VARCHAR(50);
        ALTER TABLE invoices ADD COLUMN IF NOT EXISTS customer_name VARCHAR(150);
        ALTER TABLE invoices ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(50);
        ALTER TABLE invoices ADD COLUMN IF NOT EXISTS customer_email VARCHAR(150);
        ALTER TABLE invoices ADD COLUMN IF NOT EXISTS customer_address VARCHAR(300);
        ALTER TABLE invoices ADD COLUMN IF NOT EXISTS created_at VARCHAR(50);
        ALTER TABLE invoices ADD COLUMN IF NOT EXISTS items_count INTEGER DEFAULT 0;
        ALTER TABLE invoices ADD COLUMN IF NOT EXISTS grand_total DOUBLE PRECISION DEFAULT 0.0;
        ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50);
        ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_status VARCHAR(50);
    """))
    conn.execute(text("""
        UPDATE invoices SET
            invoice_number = COALESCE(payload->>'invoice_number', ''),
            customer_name = COALESCE(payload->>'customer_name', ''),
            customer_phone = COALESCE(payload->>'customer_phone', ''),
            customer_email = COALESCE(payload->>'customer_email', ''),
            customer_address = COALESCE(payload->>'customer_address', ''),
            created_at = COALESCE(payload->>'created_at', ''),
            items_count = CASE WHEN payload->>'items_count' IS NOT NULL AND payload->>'items_count' != '' THEN (payload->>'items_count')::int ELSE 1 END,
            grand_total = CASE WHEN payload->>'grand_total' IS NOT NULL AND payload->>'grand_total' != '' THEN (payload->>'grand_total')::float ELSE 0.0 END,
            payment_method = COALESCE(payload->>'payment_method', 'Cash'),
            payment_status = COALESCE(payload->>'payment_status', 'Paid')
        WHERE payload IS NOT NULL;
    """))
    print("invoices columns added and backfilled.")

    # 3. invoice_items
    conn.execute(text("""
        ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS invoice_id VARCHAR(100);
        ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS product_id VARCHAR(100);
        ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS product_name VARCHAR(255);
        ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS sku VARCHAR(100);
        ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS quantity DOUBLE PRECISION DEFAULT 1;
        ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS unit_price DOUBLE PRECISION DEFAULT 0;
        ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS mrp DOUBLE PRECISION DEFAULT 0;
    """))
    conn.execute(text("""
        UPDATE invoice_items SET
            invoice_id = COALESCE(payload->>'invoice_id', ''),
            product_id = COALESCE(payload->>'product_id', ''),
            product_name = COALESCE(payload->>'product_name_snapshot', ''),
            sku = COALESCE(payload->>'sku_snapshot', ''),
            quantity = CASE WHEN payload->>'quantity' IS NOT NULL AND payload->>'quantity' != '' THEN (payload->>'quantity')::float ELSE 1.0 END,
            unit_price = CASE WHEN payload->>'unit_price' IS NOT NULL AND payload->>'unit_price' != '' THEN (payload->>'unit_price')::float ELSE 0.0 END,
            mrp = CASE WHEN payload->>'mrp' IS NOT NULL AND payload->>'mrp' != '' THEN (payload->>'mrp')::float ELSE 0.0 END
        WHERE payload IS NOT NULL;
    """))
    print("invoice_items columns added and backfilled.")

print("All billing tables updated with explicit readable columns in PostgreSQL!")
