from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from datetime import datetime
from db.database import Base

class StoreTable(Base):
    __abstract__ = True
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class Role(Base):
    __tablename__ = "roles"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class RolePermission(Base):
    __tablename__ = "role_permissions"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class Department(Base):
    __tablename__ = "departments"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class CostCentre(Base):
    __tablename__ = "cost_centres"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class WarehouseLocation(Base):
    __tablename__ = "warehouse_locations"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class ItemCategory(Base):
    __tablename__ = "item_categories"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class Brand(Base):
    __tablename__ = "brands"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class UnitOfMeasure(Base):
    __tablename__ = "units_of_measure"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class UnitConversion(Base):
    __tablename__ = "unit_conversions"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class TaxRate(Base):
    __tablename__ = "tax_rates"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class Item(Base):
    __tablename__ = "items"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class ItemBatch(Base):
    __tablename__ = "item_batches"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class ItemSerial(Base):
    __tablename__ = "item_serials"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class SupplierContact(Base):
    __tablename__ = "supplier_contacts"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class SupplierBankAccount(Base):
    __tablename__ = "supplier_bank_accounts"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class Indent(Base):
    __tablename__ = "indents"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class IndentItem(Base):
    __tablename__ = "indent_items"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class ApprovalAction(Base):
    __tablename__ = "approval_actions"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class RFQ(Base):
    __tablename__ = "rfqs"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class RFQItem(Base):
    __tablename__ = "rfq_items"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class RFQSupplier(Base):
    __tablename__ = "rfq_suppliers"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class Quotation(Base):
    __tablename__ = "quotations"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class QuotationItem(Base):
    __tablename__ = "quotation_items"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class POItem(Base):
    __tablename__ = "po_items"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class GRNItem(Base):
    __tablename__ = "grn_items"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class QualityInspection(Base):
    __tablename__ = "quality_inspections"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class InventoryLedger(Base):
    __tablename__ = "inventory_ledger"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class InventoryBalance(Base):
    __tablename__ = "inventory_balances"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class StockIssue(Base):
    __tablename__ = "stock_issues"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class StockIssueItem(Base):
    __tablename__ = "stock_issue_items"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class StockReturn(Base):
    __tablename__ = "stock_returns"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class SupplierReturn(Base):
    __tablename__ = "supplier_returns"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class StockTransfer(Base):
    __tablename__ = "stock_transfers"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class StockTransferItem(Base):
    __tablename__ = "stock_transfer_items"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class StockCountSession(Base):
    __tablename__ = "stock_count_sessions"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class StockCountEntry(Base):
    __tablename__ = "stock_count_entries"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class StockReservation(Base):
    __tablename__ = "stock_reservations"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class OTPVerification(Base):
    __tablename__ = "otps"
    id = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

class SystemSetting(Base):
    __tablename__ = "settings"
    key = Column(String(100), primary_key=True, index=True)
    payload = Column(JSON, nullable=False, default={})

TABLE_MODEL_MAP = {
    "users": User,
    "roles": Role,
    "permissions": Permission,
    "role_permissions": RolePermission,
    "departments": Department,
    "cost_centres": CostCentre,
    "warehouses": Warehouse,
    "warehouse_locations": WarehouseLocation,
    "item_categories": ItemCategory,
    "brands": Brand,
    "units_of_measure": UnitOfMeasure,
    "unit_conversions": UnitConversion,
    "tax_rates": TaxRate,
    "items": Item,
    "item_batches": ItemBatch,
    "item_serials": ItemSerial,
    "suppliers": Supplier,
    "supplier_contacts": SupplierContact,
    "supplier_bank_accounts": SupplierBankAccount,
    "indents": Indent,
    "indent_items": IndentItem,
    "approval_workflows": ApprovalWorkflow,
    "approval_requests": ApprovalRequest,
    "approval_actions": ApprovalAction,
    "rfqs": RFQ,
    "rfq_items": RFQItem,
    "rfq_suppliers": RFQSupplier,
    "quotations": Quotation,
    "quotation_items": QuotationItem,
    "purchase_orders": PurchaseOrder,
    "po_items": POItem,
    "goods_receipts": GoodsReceipt,
    "grn_items": GRNItem,
    "quality_inspections": QualityInspection,
    "inventory_ledger": InventoryLedger,
    "inventory_balances": InventoryBalance,
    "stock_issues": StockIssue,
    "stock_issue_items": StockIssueItem,
    "stock_returns": StockReturn,
    "supplier_returns": SupplierReturn,
    "stock_transfers": StockTransfer,
    "stock_transfer_items": StockTransferItem,
    "stock_adjustments": StockAdjustment,
    "stock_count_sessions": StockCountSession,
    "stock_count_entries": StockCountEntry,
    "stock_reservations": StockReservation,
    "assets": Asset,
    "notifications": Notification,
    "audit_logs": AuditLog,
    "otps": OTPVerification
}
