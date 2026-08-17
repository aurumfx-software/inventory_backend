from fastapi import APIRouter
from db.database_store import db
from datetime import datetime

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/{report_type}")
def get_report(report_type: str):
    data = []

    if report_type in ["current-stock", "stock-valuation"]:
        for bal in db["inventory_balances"]:
            item = next((i for i in db["items"] if i["id"] == bal["item_id"]), {})
            wh = next((w for w in db["warehouses"] if w["id"] == bal["warehouse_id"]), {})
            data.append({
                "item_code": item.get("item_code", "N/A"),
                "item_name": item.get("item_name", "N/A"),
                "warehouse": wh.get("name", "N/A"),
                "on_hand_qty": bal.get("on_hand_qty", 0),
                "reserved_qty": bal.get("reserved_qty", 0),
                "available_qty": bal.get("available_qty", 0),
                "valuation_rate": bal.get("valuation_rate", 0),
                "total_value": bal.get("on_hand_qty", 0) * bal.get("valuation_rate", 0)
            })

    elif report_type == "low-stock":
        for item in db["items"]:
            bal = next((b for b in db["inventory_balances"] if b["item_id"] == item["id"]), {})
            avail = bal.get("available_qty", 0)
            reorder = item.get("reorder_level", 10)
            if avail <= reorder:
                data.append({
                    "item_code": item.get("item_code"),
                    "item_name": item.get("item_name"),
                    "available_qty": avail,
                    "reorder_level": reorder,
                    "reorder_qty": item.get("reorder_qty", 15),
                    "status": "CRITICAL" if avail == 0 else "WARNING"
                })

    elif report_type == "supplier-performance":
        for sup in db["suppliers"]:
            data.append({
                "supplier_code": sup.get("supplier_code"),
                "supplier_name": sup.get("supplier_name"),
                "rating": sup.get("rating", 4.5),
                "lead_time_days": sup.get("delivery_lead_time_days", 5),
                "payment_terms": sup.get("payment_terms", "Net 30"),
                "status": sup.get("approval_status", "Approved")
            })

    else:
        data = [
            {"ref_no": "REP-2026-001", "date": datetime.now().strftime("%Y-%m-%d"), "item": "Dell Latitude 5440 Laptop", "qty": 10, "value": 720000, "status": "Completed"},
            {"ref_no": "REP-2026-002", "date": datetime.now().strftime("%Y-%m-%d"), "item": "Cat6 Ethernet Cable Drum", "qty": 50, "value": 2250, "status": "In Progress"}
        ]

    return {"success": True, "data": data}
