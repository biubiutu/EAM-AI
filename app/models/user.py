from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), comment="真实姓名")
    email = Column(String(100), comment="邮箱")
    phone = Column(String(20), comment="手机号")
    role = Column(String(20), default="engineer", comment="角色: engineer/supervisor/purchaser/leader/admin")
    is_active = Column(Boolean, default=True, comment="是否激活")

    skill_records = relationship("SkillRecord", back_populates="user")
    exam_records = relationship("ExamRecord", back_populates="user")


class SkillRecord(Base, TimestampMixin):
    __tablename__ = "skill_records"

    user_id = Column(Integer, nullable=False, comment="用户ID")
    skill_dimension = Column(String(50), nullable=False, comment="技能维度: 电气/机械/液压/PLC/安全规范")
    score = Column(Integer, default=0, comment="技能评分(0-100)")

    user = relationship("User", back_populates="skill_records")


class ExamRecord(Base, TimestampMixin):
    __tablename__ = "exam_records"

    user_id = Column(Integer, nullable=False, comment="用户ID")
    exam_type = Column(String(50), comment="考核类型: virtual_fault/dialogue")
    scenario = Column(String(500), comment="考核场景描述")
    total_score = Column(Integer, comment="总得分")
    detail = Column(String(2000), comment="考核详情JSON")
    status = Column(String(20), default="in_progress", comment="状态: in_progress/completed")

    user = relationship("User", back_populates="exam_records")