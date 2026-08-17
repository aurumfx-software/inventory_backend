from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict

class LoginRequest(BaseModel):
    email: str
    password: str

class RoleSwitchRequest(BaseModel):
    role_id: str

class ItemCreate(BaseModel):
    item_code: Optional[str] = None
    item_name: str
    description: Optional[str] = ""
    category_id: Optional[str] = None
    brand_id: Optional[str] = None
    uom_id: Optional[str] = None
    purchase_uom_id: Optional[str] = None
    tax_rate_id: Optional[str] = None
    hsn_sac_code: Optional[str] = ""
    min_stock_level: Optional[float] = 0
    max_stock_level: Optional[float] = 0
    reorder_level: Optional[float] = 0
    reorder_qty: Optional[float] = 0
    valuation_rate: Optional[float] = 0.0
    default_location_id: Optional[str] = None
    is_batch_tracked: Optional[bool] = False
    is_serial_tracked: Optional[bool] = False
    is_expiry_tracked: Optional[bool] = False
    barcode: Optional[str] = ""
    image_url: Optional[str] = ""

class SupplierCreate(BaseModel):
    supplier_code: Optional[str] = None
    supplier_name: str
    contact_person: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    address_registered: Optional[str] = ""
    gst_number: Optional[str] = ""
    pan_number: Optional[str] = ""
    payment_terms: Optional[str] = "Net 30"
    delivery_lead_time_days: Optional[int] = 5

class IndentCreate(BaseModel):
    purpose: str
    department_id: Optional[str] = "dept-01"
    required_date: Optional[str] = None
    priority: Optional[str] = "Medium"
    cost_centre: Optional[str] = "IT-001"
    remarks: Optional[str] = ""
    items: Optional[List[Dict[str, Any]]] = []

class POCreate(BaseModel):
    supplier_id: str
    po_date: Optional[str] = None
    delivery_date: Optional[str] = None
    payment_terms: Optional[str] = "Net 30"
    items: List[Dict[str, Any]]

class GRNCreate(BaseModel):
    po_id: str
    supplier_id: str
    warehouse_id: str
    received_date: Optional[str] = None
    items: List[Dict[str, Any]]
