from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Equipment(Base, TimestampMixin):
    __tablename__ = "equipments"

    code = Column(String(50), unique=True, nullable=False, comment="设备编码")
    name = Column(String(200), nullable=False, comment="设备名称")
    model = Column(String(100), comment="设备型号")
    category = Column(String(100), comment="设备分类")
    factory_code = Column(String(50), comment="所属厂区")
    workshop = Column(String(100), comment="所属车间")
    line = Column(String(100), comment="所属产线")
    status = Column(String(20), default="running", comment="状态: running/stopped/maintenance/scrapped")
    purchase_date = Column(String(20), comment="采购日期")
    warranty_expiry = Column(String(20), comment="质保到期日")
    manufacturer = Column(String(200), comment="制造商")
    supplier_id = Column(Integer, comment="供应商ID")

    bom_items = relationship("BOMItem", back_populates="equipment")
    work_orders = relationship("WorkOrder", back_populates="equipment")


class BOMItem(Base, TimestampMixin):
    __tablename__ = "bom_items"

    equipment_id = Column(Integer, ForeignKey("equipments.id"), nullable=False, comment="设备ID")
    spare_part_id = Column(Integer, ForeignKey("spare_parts.id"), nullable=False, comment="备件ID")
    quantity = Column(Integer, default=1, comment="标准用量")
    is_critical = Column(Integer, default=0, comment="是否关键备件")
    position = Column(String(100), comment="安装位置")
    ai_confidence = Column(Float, comment="AI置信度(0-1)")
    ai_evidence = Column(JSON, comment="AI证据来源")
    is_suspected_outdated = Column(Integer, default=0, comment="是否疑似过时")

    equipment = relationship("Equipment", back_populates="bom_items")
    spare_part = relationship("SparePart", back_populates="bom_items")