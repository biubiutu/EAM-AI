from sqlalchemy import Column, String, Integer, Float, Text, JSON, Date
from app.models.base import Base, TimestampMixin


class ApprovalRecord(Base, TimestampMixin):
    __tablename__ = "审批记录"

    审批单号 = Column("审批单号", String(50), unique=True, nullable=False, comment="审批单号")
    业务类型 = Column("业务类型", String(50), nullable=False, comment="业务类型")
    业务ID = Column("业务ID", Integer, nullable=False, comment="业务ID")
    申请人ID = Column("申请人ID", Integer, comment="申请人ID")
    审批人ID = Column("审批人ID", Integer, comment="审批人ID")
    AI审批摘要 = Column("AI审批摘要", Text, comment="AI审批摘要")
    AI建议 = Column("AI建议", String(50), comment="AI建议")
    AI分析详情 = Column("AI分析详情", JSON, comment="AI分析详情")
    审批人决策 = Column("审批人决策", String(20), comment="审批人决策")
    审批意见 = Column("审批意见", Text, comment="审批意见")
    审批状态 = Column("审批状态", String(20), default="pending", comment="状态")


class CostAnalysis(Base, TimestampMixin):
    __tablename__ = "成本分析"

    设备ID = Column("设备ID", Integer, nullable=False, comment="设备ID")
    采购成本 = Column("采购成本", Float, default=0, comment="采购成本")
    累计维修人工 = Column("累计维修人工", Float, default=0, comment="累计维修人工")
    累计备件消耗 = Column("累计备件消耗", Float, default=0, comment="累计备件消耗")
    累计停机损失 = Column("累计停机损失", Float, default=0, comment="累计停机损失")
    LCC全生命周期成本 = Column("LCC全生命周期成本", Float, default=0, comment="LCC全生命周期成本")
    AI健康度评分 = Column("AI健康度评分", Integer, comment="AI健康度评分")
    AI建议 = Column("AI建议", Text, comment="AI建议")
    AI详细报告 = Column("AI详细报告", JSON, comment="AI详细报告")
    分析日期 = Column("分析日期", Date, comment="分析日期")
