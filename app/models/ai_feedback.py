from sqlalchemy import Column, String, Integer, Text, JSON, Boolean
from app.models.base import Base, TimestampMixin


class AIFeedback(Base, TimestampMixin):
    """AI回答评测"""
    __tablename__ = "AI回答评测"

    用户ID = Column("用户ID", Integer, nullable=False, comment="用户ID")
    场景 = Column("场景", String(50), nullable=False, comment="场景(knowledge/diagnosis/approval)")
    问题 = Column("问题", Text, comment="用户问题")
    AI回答 = Column("AI回答", Text, comment="AI原始回答")
    引用片段JSON = Column("引用片段JSON", JSON, comment="引用片段列表")
    评分 = Column("评分", Integer, default=3, comment="评分1-5")
    是否准确 = Column("是否准确", Boolean, default=True, comment="是否准确")
    工程师纠错 = Column("工程师纠错", Text, comment="工程师纠错文本")
    状态 = Column("状态", String(20), default="pending", comment="状态(pending/approved/rejected)")