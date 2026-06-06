from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class WorkOrder(Base, TimestampMixin):
    __tablename__ = "工单"

    工单号 = Column("工单号", String(50), unique=True, nullable=False, comment="工单号")
    设备ID = Column("设备ID", Integer, ForeignKey("设备.id"), nullable=False, comment="设备ID")
    故障现象 = Column("故障现象", Text, comment="故障现象")
    故障原因 = Column("故障原因", Text, comment="故障原因")
    AI诊断置信度 = Column("AI诊断置信度", Float, comment="AI诊断置信度")
    处理措施 = Column("处理措施", Text, comment="处理措施")
    更换备件列表 = Column("更换备件列表", JSON, comment="更换备件列表")
    耗时分钟 = Column("耗时分钟", Integer, comment="耗时(分钟)")
    语音转译文本 = Column("语音转译文本", Text, comment="语音转译文本")
    故障照片URL列表 = Column("故障照片URL列表", JSON, comment="故障照片URL列表")
    AI维修报告 = Column("AI维修报告", Text, comment="AI维修报告")
    工单状态 = Column("工单状态", String(20), default="pending", comment="状态")
    维修人员ID = Column("维修人员ID", Integer, comment="维修人员ID")
    创建人ID = Column("创建人ID", Integer, comment="创建人ID")

    equipment = relationship("Equipment", back_populates="work_orders")


class InspectionRecord(Base, TimestampMixin):
    __tablename__ = "巡检记录"

    设备ID = Column("设备ID", Integer, ForeignKey("设备.id"), nullable=False, comment="设备ID")
    巡检人员ID = Column("巡检人员ID", Integer, comment="巡检人员ID")
    巡检路线 = Column("巡检路线", String(100), comment="巡检路线")
    NFC标签 = Column("NFC标签", String(100), comment="NFC标签")
    是否正常 = Column("是否正常", Integer, default=1, comment="是否正常")
    异常描述 = Column("异常描述", Text, comment="异常描述")
    异常照片 = Column("异常照片", String(500), comment="异常照片")
    关联工单ID = Column("关联工单ID", Integer, comment="关联工单ID")


class MaintenancePlan(Base, TimestampMixin):
    __tablename__ = "维护计划"

    设备ID = Column("设备ID", Integer, ForeignKey("设备.id"), nullable=False, comment="设备ID")
    计划类型 = Column("计划类型", String(50), comment="计划类型")
    预测失效时间 = Column("预测失效时间", String(50), comment="预测失效时间")
    AI预测描述 = Column("AI预测描述", Text, comment="AI预测描述")
    AI建议措施 = Column("AI建议措施", Text, comment="AI建议措施")
    建议更换备件 = Column("建议更换备件", String(200), comment="建议更换备件")
    计划状态 = Column("计划状态", String(20), default="pending", comment="状态")
