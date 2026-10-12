import urllib.request
import json

def test_pos_billing():
    # 1. Test next bill number
    res = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/billing/invoice-number').read())
    expected_bill_no = res['invoice_number']
    print('1. NEXT AVAILABLE BILL NUMBER:', expected_bill_no)
    assert expected_bill_no.startswith('SH/25-27/'), 'Bill number prefix must be SH/25-27/'
    seq = int(expected_bill_no.split('/')[-1])
    next_expected_bill_no = f"SH/25-27/{str(seq + 1).zfill(7)}"

    # 2. Test barcode search
    res = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/billing/products/search?q=890100000001').read())
    p1 = res['data'][0]
    print('2. BARCODE SEARCH RESULT:', p1['name'], '| SKU:', p1['sku'], '| Stock:', p1['available_stock'])
    initial_stock = p1['available_stock']

    # 3. Create invoice with 2 units of p1
    req_data = {
        'customer': {'name': 'Walk-in Customer', 'phone': '9895000001', 'is_walk_in': True},
        'items': [{
            'product_id': p1['id'],
            'quantity': 2,
            'unit_price': p1['unit_price'],
            'mrp': p1['mrp'],
            'discount': 0.0,
            'warehouse_id': 'wh-01'
        }],
        'payment_method': 'Cash',
        'amount_paid': p1['unit_price'] * 2 + 100, # cash with change
        'sale_type': 'intra',
        'notes': 'Automated verification bill'
    }
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/billing/invoices',
        data=json.dumps(req_data).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'x-user-email': 'admin@company.com'}
    )
    inv_res = json.loads(urllib.request.urlopen(req).read())
    inv = inv_res['data']['invoice']
    print('3. CREATED INVOICE NUMBER:', inv['invoice_number'])
    print('   Grand Total:', inv['grand_total'])
    print('   Amount Paid:', inv['amount_paid'])
    print('   Change:', inv['change_amount'])
    print('   Savings:', inv['savings'])
    assert inv['invoice_number'] == expected_bill_no, f"Created invoice number must be {expected_bill_no}"

    # 4. Check stock reduction
    res = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/billing/products/search?q=890100000001').read())
    new_stock = res['data'][0]['available_stock']
    print(f'4. STOCK BEFORE: {initial_stock} -> AFTER: {new_stock} (Deducted {initial_stock - new_stock})')
    assert new_stock == initial_stock - 2, f'Stock must decrease by 2 (expected {initial_stock - 2}, got {new_stock})'

    # 5. Check next sequential bill number
    res = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/billing/invoice-number').read())
    print('5. NEXT SEQUENTIAL BILL NUMBER:', res['invoice_number'])
    assert res['invoice_number'] == next_expected_bill_no, f"Next invoice number must be {next_expected_bill_no}"

    # 6. Verify in Billing History
    res = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/billing/invoices').read())
    latest = res['data'][0]
    print('6. BILLING HISTORY LATEST:', latest['invoice_number'], '| Total:', latest['grand_total'], '| Status:', latest['payment_status'])
    assert latest['invoice_number'] == expected_bill_no

    print('\n======================================================')
    print(' ALL POS BILLING VERIFICATION CHECKS PASSED!')
    print('======================================================')

if __name__ == '__main__':
    test_pos_billing()
