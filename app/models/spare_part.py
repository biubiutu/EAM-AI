from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class SparePart(Base, TimestampMixin):
    __tablename__ = "备件"

    SKU编码 = Column("SKU编码", String(50), unique=True, nullable=False, comment="SKU编码")
    备件名称 = Column("备件名称", String(200), nullable=False, comment="备件名称")
    规格型号 = Column("规格型号", String(500), comment="规格型号")
    分类 = Column("分类", String(100), comment="分类")
    单位 = Column("单位", String(20), default="个", comment="单位")
    参考单价 = Column("参考单价", Float, comment="参考单价")
    保质期天数 = Column("保质期天数", Integer, comment="保质期(天)")
    最小库存 = Column("最小库存", Integer, default=0, comment="最小库存")
    最大库存 = Column("最大库存", Integer, default=0, comment="最大库存")
    安全库存 = Column("安全库存", Integer, default=0, comment="安全库存")

    bom_items = relationship("BOMItem", back_populates="spare_part")
    inventory_records = relationship("InventoryRecord", back_populates="spare_part")


class Warehouse(Base, TimestampMixin):
    __tablename__ = "仓库"

    仓库编码 = Column("仓库编码", String(50), unique=True, nullable=False, comment="仓库编码")
    仓库名称 = Column("仓库名称", String(200), nullable=False, comment="仓库名称")
    所属厂区 = Column("所属厂区", String(50), comment="所属厂区")
    地址 = Column("地址", String(500), comment="地址")
    负责人ID = Column("负责人ID", Integer, comment="负责人ID")

    inventory_records = relationship("InventoryRecord", back_populates="warehouse")


class InventoryRecord(Base, TimestampMixin):
    __tablename__ = "库存记录"

    备件ID = Column("备件ID", Integer, ForeignKey("备件.id"), nullable=False, comment="备件ID")
    仓库ID = Column("仓库ID", Integer, ForeignKey("仓库.id"), nullable=False, comment="仓库ID")
    库位编码 = Column("库位编码", String(50), comment="库位编码")
    账面数量 = Column("账面数量", Integer, default=0, comment="账面数量")
    可用数量 = Column("可用数量", Integer, default=0, comment="可用数量")
    预留数量 = Column("预留数量", Integer, default=0, comment="预留数量")
    预留用途 = Column("预留用途", String(200), comment="预留用途")
    批次号 = Column("批次号", String(50), comment="批次号")
    生产日期 = Column("生产日期", DateTime, comment="生产日期")
    过期日期 = Column("过期日期", DateTime, comment="过期日期")

    spare_part = relationship("SparePart", back_populates="inventory_records")
    warehouse = relationship("Warehouse", back_populates="inventory_records")


class Requisition(Base, TimestampMixin):
    __tablename__ = "申购单"

    申购单号 = Column("申购单号", String(50), unique=True, nullable=False, comment="申购单号")
    备件ID = Column("备件ID", Integer, ForeignKey("备件.id"), nullable=False, comment="备件ID")
    申请人ID = Column("申请人ID", Integer, comment="申请人ID")
    申请数量 = Column("申请数量", Integer, nullable=False, comment="申请数量")
    AI推荐数量 = Column("AI推荐数量", Integer, comment="AI推荐数量")
    AI推荐理由 = Column("AI推荐理由", Text, comment="AI推荐理由")
    AI审核状态 = Column("AI审核状态", String(20), comment="AI审核状态")
    AI审核详情 = Column("AI审核详情", JSON, comment="AI审核详情")
    偏离原因 = Column("偏离原因", String(100), comment="偏离原因")
    偏离补充说明 = Column("偏离补充说明", Text, comment="偏离补充说明")
    关联工单ID = Column("关联工单ID", Integer, comment="关联工单ID")
    申购状态 = Column("申购状态", String(20), default="pending", comment="状态")

    spare_part = relationship("SparePart")


class TransferOrder(Base, TimestampMixin):
    __tablename__ = "调拨单"

    调拨单号 = Column("调拨单号", String(50), unique=True, nullable=False, comment="调拨单号")
    备件ID = Column("备件ID", Integer, ForeignKey("备件.id"), nullable=False, comment="备件ID")
    调出仓库ID = Column("调出仓库ID", Integer, ForeignKey("仓库.id"), nullable=False, comment="调出仓库")
    调入仓库ID = Column("调入仓库ID", Integer, ForeignKey("仓库.id"), nullable=False, comment="调入仓库")
    调拨数量 = Column("调拨数量", Integer, nullable=False, comment="调拨数量")
    AI可行性打分 = Column("AI可行性打分", Float, comment="AI可行性打分")
    AI分析详情 = Column("AI分析详情", JSON, comment="AI分析详情")
    调拨总成本 = Column("调拨总成本", Float, comment="调拨总成本")
    缺货停工等待成本 = Column("缺货停工等待成本", Float, comment="缺货停工等待成本")
    净收益 = Column("净收益", Float, comment="净收益")
    AI建议 = Column("AI建议", Text, comment="AI建议")
    调拨状态 = Column("调拨状态", String(20), default="pending", comment="状态")

    spare_part = relationship("SparePart")
    from_warehouse = relationship("Warehouse", foreign_keys=[调出仓库ID])
    to_warehouse = relationship("Warehouse", foreign_keys=[调入仓库ID])


class StagnantAlert(Base, TimestampMixin):
    __tablename__ = "呆滞预警"

    备件ID = Column("备件ID", Integer, ForeignKey("备件.id"), nullable=False, comment="备件ID")
    仓库ID = Column("仓库ID", Integer, ForeignKey("仓库.id"), nullable=False, comment="仓库ID")
    呆滞数量 = Column("呆滞数量", Integer, comment="呆滞数量")
    呆滞天数 = Column("呆滞天数", Integer, comment="呆滞天数")
    AI预测即将呆滞天数 = Column("AI预测即将呆滞天数", Integer, comment="AI预测即将呆滞天数")
    AI处理建议 = Column("AI处理建议", Text, comment="AI处理建议")
    调拨建议 = Column("调拨建议", JSON, comment="调拨建议")
    预警状态 = Column("预警状态", String(20), default="active", comment="状态")
