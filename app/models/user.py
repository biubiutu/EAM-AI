from sqlalchemy import Column, String, Integer, Boolean
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "用户"

    用户名 = Column("用户名", String(50), unique=True, nullable=False, comment="用户名")
    密码哈希 = Column("密码哈希", String(255), nullable=False, comment="密码哈希")
    真实姓名 = Column("真实姓名", String(50), comment="真实姓名")
    邮箱 = Column("邮箱", String(100), comment="邮箱")
    手机号 = Column("手机号", String(20), comment="手机号")
    角色 = Column("角色", String(20), default="engineer", comment="角色")
    是否激活 = Column("是否激活", Boolean, default=True, comment="是否激活")


class SkillRecord(Base, TimestampMixin):
    __tablename__ = "技能记录"

    用户ID = Column("用户ID", Integer, nullable=False, comment="用户ID")
    技能维度 = Column("技能维度", String(50), nullable=False, comment="技能维度")
    技能评分 = Column("技能评分", Integer, default=0, comment="技能评分(0-100)")


class ExamRecord(Base, TimestampMixin):
    __tablename__ = "考核记录"

    用户ID = Column("用户ID", Integer, nullable=False, comment="用户ID")
    考核类型 = Column("考核类型", String(50), comment="考核类型")
    考核场景 = Column("考核场景", String(500), comment="考核场景描述")
    总得分 = Column("总得分", Integer, comment="总得分")
    考核详情 = Column("考核详情", String(2000), comment="考核详情JSON")
    状态 = Column("状态", String(20), default="in_progress", comment="状态")
