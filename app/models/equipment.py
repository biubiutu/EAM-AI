from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Equipment(Base, TimestampMixin):
    __tablename__ = "设备"

    设备编码 = Column("设备编码", String(50), unique=True, nullable=False, comment="设备编码")
    设备名称 = Column("设备名称", String(200), nullable=False, comment="设备名称")
    设备型号 = Column("设备型号", String(100), comment="设备型号")
    设备分类 = Column("设备分类", String(100), comment="设备分类")
    所属厂区 = Column("所属厂区", String(50), comment="所属厂区")
    所属车间 = Column("所属车间", String(100), comment="所属车间")
    所属产线 = Column("所属产线", String(100), comment="所属产线")
    设备状态 = Column("设备状态", String(20), default="running", comment="状态")
    采购日期 = Column("采购日期", String(20), comment="采购日期")
    质保到期日 = Column("质保到期日", String(20), comment="质保到期日")
    制造商 = Column("制造商", String(200), comment="制造商")
    供应商ID = Column("供应商ID", Integer, comment="供应商ID")

    bom_items = relationship("BOMItem", back_populates="equipment")
    work_orders = relationship("WorkOrder", back_populates="equipment")


class BOMItem(Base, TimestampMixin):
    __tablename__ = "bom清单"  # Windows MySQL lower_case_table_names 会将 BOM清单 存为小写

    设备ID = Column("设备ID", Integer, ForeignKey("设备.id"), nullable=False, comment="设备ID")
    备件ID = Column("备件ID", Integer, ForeignKey("备件.id"), nullable=False, comment="备件ID")
    标准用量 = Column("标准用量", Integer, default=1, comment="标准用量")
    是否关键备件 = Column("是否关键备件", Integer, default=0, comment="是否关键备件")
    安装位置 = Column("安装位置", String(100), comment="安装位置")
    AI置信度 = Column("AI置信度", Float, comment="AI置信度")
    AI证据来源 = Column("AI证据来源", JSON, comment="AI证据来源")
    是否疑似过时 = Column("是否疑似过时", Integer, default=0, comment="是否疑似过时")

    equipment = relationship("Equipment", back_populates="bom_items")
    spare_part = relationship("SparePart", back_populates="bom_items")
