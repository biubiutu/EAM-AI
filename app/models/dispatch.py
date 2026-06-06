from sqlalchemy import Column, String, Integer, Float, Text
from app.models.base import Base, TimestampMixin


class EngineerDispatch(Base, TimestampMixin):
    __tablename__ = "工程师调派"

    工程师ID = Column("工程师ID", Integer, nullable=False, comment="工程师用户ID")
    工程师姓名 = Column("工程师姓名", String(50), comment="工程师姓名")
    工程师技能 = Column("工程师技能", String(500), comment="工程师技能等级JSON")
    维修地点 = Column("维修地点", String(200), nullable=False, comment="维修地点")
    距离公里 = Column("距离公里", Float, default=0, comment="距离(km)")
    任务描述 = Column("任务描述", Text, comment="任务描述")
    调派状态 = Column("调派状态", String(20), default="dispatched", comment="状态")
    主管ID = Column("主管ID", Integer, comment="主管用户ID")
    主管姓名 = Column("主管姓名", String(50), comment="主管姓名")
