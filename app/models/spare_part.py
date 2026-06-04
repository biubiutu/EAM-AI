from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class SparePart(Base, TimestampMixin):
    __tablename__ = "spare_parts"

    sku_code = Column(String(50), unique=True, nullable=False, comment="SKU编码")
    name = Column(String(200), nullable=False, comment="备件名称")
    specification = Column(String(500), comment="规格型号")
    category = Column(String(100), comment="分类")
    unit = Column(String(20), default="个", comment="单位")
    unit_price = Column(Float, comment="参考单价")
    shelf_life_days = Column(Integer, comment="保质期(天)")
    min_stock = Column(Integer, default=0, comment="最小库存")
    max_stock = Column(Integer, default=0, comment="最大库存")
    safety_stock = Column(Integer, default=0, comment="安全库存")

    bom_items = relationship("BOMItem", back_populates="spare_part")
    inventory_records = relationship("InventoryRecord", back_populates="spare_part")


class Warehouse(Base, TimestampMixin):
    __tablename__ = "warehouses"

    code = Column(String(50), unique=True, nullable=False, comment="仓库编码")
    name = Column(String(200), nullable=False, comment="仓库名称")
    factory_code = Column(String(50), comment="所属厂区")
    address = Column(String(500), comment="地址")
    manager_id = Column(Integer, comment="负责人ID")

    inventory_records = relationship("InventoryRecord", back_populates="warehouse")


class InventoryRecord(Base, TimestampMixin):
    __tablename__ = "inventory_records"

    spare_part_id = Column(Integer, ForeignKey("spare_parts.id"), nullable=False, comment="备件ID")
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="仓库ID")
    location_code = Column(String(50), comment="库位编码")
    quantity = Column(Integer, default=0, comment="账面数量")
    available_quantity = Column(Integer, default=0, comment="可用数量")
    reserved_quantity = Column(Integer, default=0, comment="预留数量")
    reserved_for = Column(String(200), comment="预留用途")
    batch_no = Column(String(50), comment="批次号")
    production_date = Column(DateTime, comment="生产日期")
    expiry_date = Column(DateTime, comment="过期日期")

    spare_part = relationship("SparePart", back_populates="inventory_records")
    warehouse = relationship("Warehouse", back_populates="inventory_records")


class Requisition(Base, TimestampMixin):
    __tablename__ = "requisitions"

    requisition_no = Column(String(50), unique=True, nullable=False, comment="申购单号")
    spare_part_id = Column(Integer, ForeignKey("spare_parts.id"), nullable=False, comment="备件ID")
    requester_id = Column(Integer, comment="申请人ID")
    requested_quantity = Column(Integer, nullable=False, comment="申请数量")
    ai_recommended_quantity = Column(Integer, comment="AI推荐数量")
    ai_recommended_reason = Column(Text, comment="AI推荐理由")
    ai_review_status = Column(String(20), comment="AI审核状态: pass/warning/force_review")
    ai_review_detail = Column(JSON, comment="AI审核详情")
    deviation_reason = Column(String(100), comment="偏离原因")
    deviation_note = Column(Text, comment="偏离补充说明")
    work_order_id = Column(Integer, comment="关联工单ID")
    status = Column(String(20), default="pending", comment="状态: pending/approved/rejected")

    spare_part = relationship("SparePart")


class TransferOrder(Base, TimestampMixin):
    __tablename__ = "transfer_orders"

    transfer_no = Column(String(50), unique=True, nullable=False, comment="调拨单号")
    spare_part_id = Column(Integer, ForeignKey("spare_parts.id"), nullable=False, comment="备件ID")
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="调出仓库")
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="调入仓库")
    quantity = Column(Integer, nullable=False, comment="调拨数量")
    ai_feasibility_score = Column(Float, comment="AI可行性打分(0-100)")
    ai_analysis = Column(JSON, comment="AI分析详情")
    transfer_cost = Column(Float, comment="调拨总成本")
    waiting_cost = Column(Float, comment="缺货停工等待成本")
    net_benefit = Column(Float, comment="净收益")
    recommendation = Column(Text, comment="AI建议")
    status = Column(String(20), default="pending", comment="状态: pending/in_transit/completed/cancelled")

    spare_part = relationship("SparePart")
    from_warehouse = relationship("Warehouse", foreign_keys=[from_warehouse_id])
    to_warehouse = relationship("Warehouse", foreign_keys=[to_warehouse_id])


class StagnantAlert(Base, TimestampMixin):
    __tablename__ = "stagnant_alerts"

    spare_part_id = Column(Integer, ForeignKey("spare_parts.id"), nullable=False, comment="备件ID")
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="仓库ID")
    quantity = Column(Integer, comment="呆滞数量")
    stagnant_days = Column(Integer, comment="呆滞天数")
    ai_prediction_days = Column(Integer, comment="AI预测即将呆滞天数")
    ai_suggestion = Column(Text, comment="AI处理建议")
    transfer_suggestion = Column(JSON, comment="调拨建议")
    status = Column(String(20), default="active", comment="状态: active/resolved")