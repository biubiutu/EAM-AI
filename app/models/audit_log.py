from sqlalchemy import Column, String, Integer, Text, JSON
from app.models.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    """操作审计日志"""
    __tablename__ = "审计日志"

    用户ID = Column("用户ID", Integer, comment="用户ID")
    用户名 = Column("用户名", String(50), comment="用户名")
    操作类型 = Column("操作类型", String(50), nullable=False, comment="操作类型(role_change/approval/doc_level_change/equipment_status/etc)")
    操作详情 = Column("操作详情", Text, comment="操作详情JSON")
    IP地址 = Column("IP地址", String(50), comment="请求IP")