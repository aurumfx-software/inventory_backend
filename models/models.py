"""
Enterprise Inventory & Procurement System - Data Models
Defines Python Data Models for all 22 PDF Specification Entities.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

# ==========================================
# 1. USER & ACCESS CONTROL MODELS
# ==========================================

@dataclass
class UserModel:
    id: str
    name: str
    email: str
    password: str
    emp_code: str
    role_id: str
    department_id: Optional[str] = "dept-01"
    branch_id: Optional[str] = "br-01"
    company_id: Optional[str] = "comp-01"
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class RoleModel:
    id: str
    name: str
    description: Optional[str] = ""
    is_active: bool = True

@dataclass
class PermissionModel:
    id: str
    action: str
    module: str

# ==========================================
# 2. MASTER DATA MODELS
# ==========================================

@dataclass
class DepartmentModel:
    id: str
    code: str
    name: str
    head_id: Optional[str] = None
    cost_centre: Optional[str] = ""
    budget_annual: float = 0.0
    active_status: bool = True

@dataclass
class WarehouseModel:
    id: str
    code: str
    name: str
    address: Optional[str] = ""
    manager_id: Optional[str] = None
    wh_type: Optional[str] = "Central"
    active_status: bool = True

@dataclass
class WarehouseLocationModel:
    id: str
    warehouse_id: str
    zone: str
    rack: str
    shelf: str
    bin: str
    code: str
    is_active: bool = True

@dataclass
class ItemCategoryModel:
    id: str
    category_code: str
    category_name: str
    description: Optional[str] = ""
    is_active: bool = True

@dataclass
class BrandModel:
    id: str
    brand_name: str

@dataclass
class UnitOfMeasureModel:
    id: str
    unit_name: str
    unit_symbol: str
    decimal_allowed: bool = False

@dataclass
class TaxRateModel:
    id: str
    name: str
    percentage: float
    tax_type: str

@dataclass
class ItemModel:
    id: str
    item_code: str
    item_name: str
    description: Optional[str] = ""
    category_id: Optional[str] = None
    brand_id: Optional[str] = None
    uom_id: Optional[str] = None
    purchase_uom_id: Optional[str] = None
    tax_rate_id: Optional[str] = None
    hsn_sac_code: Optional[str] = ""
    min_stock_level: float = 0.0
    max_stock_level: float = 0.0
    reorder_level: float = 0.0
    reorder_qty: float = 0.0
    valuation_rate: float = 0.0
    default_location_id: Optional[str] = None
    is_batch_tracked: bool = False
    is_serial_tracked: bool = False
    is_expiry_tracked: bool = False
    barcode: Optional[str] = ""
    image_url: Optional[str] = ""
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class SupplierModel:
    id: str
    supplier_code: str
    supplier_name: str
    contact_person: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    address_registered: Optional[str] = ""
    gst_number: Optional[str] = ""
    pan_number: Optional[str] = ""
    payment_terms: str = "Net 30"
    delivery_lead_time_days: int = 5
    rating: float = 4.5
    approval_status: str = "Approved"
    is_active: bool = True

# ==========================================
# 3. PROCUREMENT & REQUISITION MODELS
# ==========================================

@dataclass
class MaterialIndentModel:
    id: str
    indent_number: str
    request_date: str
    department_id: str
    requested_by: str
    required_date: str
    purpose: str
    priority: str = "Medium"
    cost_centre: str = "IT-001"
    remarks: Optional[str] = ""
    status: str = "Submitted"
    total_estimated_amount: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ApprovalRequestModel:
    id: str
    transaction_type: str
    transaction_id: str
    approval_level: int
    approver_id: str
    assigned_date: str
    status: str = "Pending"
    comments: Optional[str] = ""

@dataclass
class RFQModel:
    id: str
    rfq_number: str
    rfq_date: str
    indent_id: str
    status: str = "Published"
    due_date: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class QuotationModel:
    id: str
    quotation_number: str
    rfq_id: str
    supplier_id: str
    quote_date: str
    total_landed_cost: float
    is_l1_selected: bool = False
    status: str = "Submitted"

@dataclass
class PurchaseOrderModel:
    id: str
    po_number: str
    po_date: str
    supplier_id: str
    rfq_id: Optional[str] = None
    payment_terms: str = "Net 30 days"
    delivery_date: str = ""
    status: str = "Approved"
    total_amount: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

# ==========================================
# 4. INVENTORY OPERATIONS & STOCK TRACKING
# ==========================================

@dataclass
class GoodsReceiptModel:
    id: str
    grn_number: str
    receipt_date: str
    po_id: str
    supplier_id: str
    warehouse_id: str
    inspection_status: str = "Inspected & Passed"
    status: str = "Posted"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class InventoryLedgerModel:
    id: str
    posting_date: str
    item_id: str
    warehouse_id: str
    voucher_type: str
    voucher_no: str
    qty_in: float
    qty_out: float
    balance_qty: float
    valuation_rate: float

@dataclass
class InventoryBalanceModel:
    id: str
    item_id: str
    warehouse_id: str
    location_id: str
    on_hand_qty: float
    reserved_qty: float
    available_qty: float
    valuation_rate: float

@dataclass
class ItemBatchModel:
    id: str
    item_id: str
    batch_number: str
    mfg_date: str
    expiry_date: str
    received_qty: float
    available_qty: float
    supplier_id: str

@dataclass
class ItemSerialModel:
    id: str
    item_id: str
    serial_number: str
    status: str = "Available"
    warehouse_id: str = "wh-01"
    assigned_employee: Optional[str] = None

@dataclass
class AssetModel:
    id: str
    asset_number: str
    item_id: str
    serial_number: str
    purchase_date: str
    purchase_value: float
    warranty_expiry: str
    assigned_employee_id: Optional[str] = None
    status: str = "Assigned"

# ==========================================
# 5. AUDIT & SYSTEM LOGS
# ==========================================

@dataclass
class AuditLogModel:
    id: str
    user_id: str
    action: str
    module: str
    record_id: str
    details: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    ip_address: str = "127.0.0.1"
