from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, JSON, Date
from app.models.base import Base, TimestampMixin


class ApprovalRecord(Base, TimestampMixin):
    __tablename__ = "approval_records"

    approval_no = Column(String(50), unique=True, nullable=False, comment="审批单号")
    business_type = Column(String(50), nullable=False, comment="业务类型: requisition/transfer/contract")
    business_id = Column(Integer, nullable=False, comment="业务ID")
    applicant_id = Column(Integer, comment="申请人ID")
    approver_id = Column(Integer, comment="审批人ID")
    ai_summary = Column(Text, comment="AI审批摘要")
    ai_recommendation = Column(String(50), comment="AI建议: approve/reject/further_check")
    ai_detail = Column(JSON, comment="AI分析详情")
    approver_decision = Column(String(20), comment="审批人决策: approved/rejected")
    approver_comment = Column(Text, comment="审批意见")
    status = Column(String(20), default="pending", comment="状态: pending/approved/rejected")


class CostAnalysis(Base, TimestampMixin):
    __tablename__ = "cost_analyses"

    equipment_id = Column(Integer, nullable=False, comment="设备ID")
    purchase_cost = Column(Float, default=0, comment="采购成本")
    total_repair_labor = Column(Float, default=0, comment="累计维修人工")
    total_parts_cost = Column(Float, default=0, comment="累计备件消耗")
    total_downtime_loss = Column(Float, default=0, comment="累计停机损失")
    lcc_total = Column(Float, default=0, comment="LCC全生命周期成本")
    ai_health_score = Column(Integer, comment="AI健康度评分(0-100)")
    ai_recommendation = Column(Text, comment="AI建议: keep/replace/maintain")
    ai_report = Column(JSON, comment="AI详细报告")
    analyzed_at = Column(Date, comment="分析日期")