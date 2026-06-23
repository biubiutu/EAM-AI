from sqlalchemy import Column, String, Integer, Text, JSON
from app.models.base import Base, TimestampMixin


class GoldenQA(Base, TimestampMixin):
    """黄金问答库 - 审核通过的优质问答对"""
    __tablename__ = "黄金问答库"

    问题 = Column("问题", Text, nullable=False, comment="标准问题")
    标准答案 = Column("标准答案", Text, nullable=False, comment="标准答案")
    引用来源 = Column("引用来源", String(500), comment="引用来源")
    场景 = Column("场景", String(50), default="knowledge", comment="场景(knowledge/diagnosis)")
    标签 = Column("标签", String(200), comment="标签列表(逗号分隔)")
    来源评测ID = Column("来源评测ID", Integer, comment="来源AI评测ID")