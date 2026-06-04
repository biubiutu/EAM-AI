from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class WorkOrder(Base, TimestampMixin):
    __tablename__ = "work_orders"

    order_no = Column(String(50), unique=True, nullable=False, comment="工单号")
    equipment_id = Column(Integer, ForeignKey("equipments.id"), nullable=False, comment="设备ID")
    fault_phenomenon = Column(Text, comment="故障现象")
    fault_cause = Column(Text, comment="故障原因(AI诊断)")
    fault_cause_confidence = Column(Float, comment="AI诊断置信度")
    action_taken = Column(Text, comment="处理措施")
    parts_replaced = Column(JSON, comment="更换备件列表")
    time_spent = Column(Integer, comment="耗时(分钟)")
    voice_text = Column(Text, comment="语音转译文本")
    photo_urls = Column(JSON, comment="故障照片URL列表")
    report_content = Column(Text, comment="AI生成的维修报告")
    status = Column(String(20), default="pending", comment="状态: pending/in_progress/completed")
    repairer_id = Column(Integer, comment="维修人员ID")
    created_by = Column(Integer, comment="创建人ID")

    equipment = relationship("Equipment", back_populates="work_orders")


class InspectionRecord(Base, TimestampMixin):
    __tablename__ = "inspection_records"

    equipment_id = Column(Integer, ForeignKey("equipments.id"), nullable=False, comment="设备ID")
    inspector_id = Column(Integer, comment="巡检人员ID")
    inspection_route = Column(String(100), comment="巡检路线")
    nfc_tag = Column(String(100), comment="NFC标签")
    is_normal = Column(Integer, default=1, comment="是否正常")
    abnormal_desc = Column(Text, comment="异常描述")
    abnormal_photo_url = Column(String(500), comment="异常照片")
    linked_work_order_id = Column(Integer, comment="关联工单ID")


class MaintenancePlan(Base, TimestampMixin):
    __tablename__ = "maintenance_plans"

    equipment_id = Column(Integer, ForeignKey("equipments.id"), nullable=False, comment="设备ID")
    plan_type = Column(String(50), comment="计划类型: preventive/predictive")
    predicted_failure_time = Column(String(50), comment="预测失效时间")
    ai_prediction = Column(Text, comment="AI预测描述")
    ai_recommendation = Column(Text, comment="AI建议措施")
    recommended_part = Column(String(200), comment="建议更换备件")
    status = Column(String(20), default="pending", comment="状态")