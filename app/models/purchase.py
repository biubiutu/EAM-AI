from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON, Date
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Supplier(Base, TimestampMixin):
    __tablename__ = "供应商"

    供应商编码 = Column("供应商编码", String(50), unique=True, nullable=False, comment="供应商编码")
    供应商名称 = Column("供应商名称", String(200), nullable=False, comment="供应商名称")
    联系人 = Column("联系人", String(100), comment="联系人")
    联系电话 = Column("联系电话", String(50), comment="联系电话")
    邮箱 = Column("邮箱", String(100), comment="邮箱")
    地址 = Column("地址", String(500), comment="地址")
    交付准时率 = Column("交付准时率", Float, comment="历史交付准时率(%)")
    质量合格率 = Column("质量合格率", Float, comment="质量合格率(%)")
    综合评分 = Column("综合评分", Float, comment="综合推荐指数(0-100)")
    风险等级 = Column("风险等级", String(20), default="low", comment="风险等级")
    风险标签 = Column("风险标签", JSON, comment="风险标签列表")
    最后风险检查时间 = Column("最后风险检查时间", DateTime, comment="最后风险检查时间")

    quotations = relationship("Quotation", back_populates="supplier")
    contracts = relationship("Contract", back_populates="supplier")
    supply_categories = relationship("SupplierCategory", back_populates="supplier")
    risk_alerts = relationship("SupplierRiskAlert", back_populates="supplier")


class SupplierCategory(Base, TimestampMixin):
    __tablename__ = "供应商品类"

    供应商ID = Column("供应商ID", Integer, ForeignKey("供应商.id"), nullable=False, comment="供应商ID")
    供应品类 = Column("供应品类", String(100), nullable=False, comment="供应品类")
    是否合格 = Column("是否合格", Integer, default=1, comment="是否合格供应商")

    supplier = relationship("Supplier", back_populates="supply_categories")


class Quotation(Base, TimestampMixin):
    __tablename__ = "报价单"

    报价单号 = Column("报价单号", String(50), unique=True, nullable=False, comment="报价单号")
    供应商ID = Column("供应商ID", Integer, ForeignKey("供应商.id"), nullable=False, comment="供应商ID")
    关联采购申请ID = Column("关联采购申请ID", Integer, comment="关联采购申请ID")
    报价明细 = Column("报价明细", JSON, comment="报价明细")
    原始文件路径 = Column("原始文件路径", String(500), comment="原始报价单文件路径")
    OCR状态 = Column("OCR状态", String(20), default="pending", comment="OCR状态")
    OCR置信度 = Column("OCR置信度", Float, comment="OCR置信度")
    报价状态 = Column("报价状态", String(20), default="received", comment="状态")

    supplier = relationship("Supplier", back_populates="quotations", foreign_keys=[供应商ID])


class PriceComparison(Base, TimestampMixin):
    __tablename__ = "比价记录"

    比价单号 = Column("比价单号", String(50), unique=True, nullable=False, comment="比价单号")
    备件ID = Column("备件ID", Integer, comment="备件ID")
    参与比价报价单ID列表 = Column("参与比价报价单ID列表", JSON, comment="参与比价的报价单ID列表")
    比价结果 = Column("比价结果", JSON, comment="比价结果")
    创建人ID = Column("创建人ID", Integer, comment="创建人ID")


class Contract(Base, TimestampMixin):
    __tablename__ = "合同"

    合同编号 = Column("合同编号", String(50), unique=True, nullable=False, comment="合同编号")
    供应商ID = Column("供应商ID", Integer, ForeignKey("供应商.id"), nullable=False, comment="供应商ID")
    合同标题 = Column("合同标题", String(300), comment="合同标题")
    文件路径 = Column("文件路径", String(500), comment="合同文件路径")
    AI审查状态 = Column("AI审查状态", String(20), default="pending", comment="AI审查状态")
    AI审查结果 = Column("AI审查结果", JSON, comment="AI审查结果")
    签订日期 = Column("签订日期", Date, comment="签订日期")
    到期日期 = Column("到期日期", Date, comment="到期日期")

    supplier = relationship("Supplier", back_populates="contracts")


class SupplierRiskAlert(Base, TimestampMixin):
    __tablename__ = "供应商风险预警"

    供应商ID = Column("供应商ID", Integer, ForeignKey("供应商.id"), nullable=False, comment="供应商ID")
    预警类型 = Column("预警类型", String(50), comment="预警类型")
    严重程度 = Column("严重程度", String(20), comment="严重程度")
    预警标题 = Column("预警标题", String(300), comment="预警标题")
    预警详情 = Column("预警详情", Text, comment="预警详情")
    信息来源 = Column("信息来源", String(500), comment="信息来源")
    AI建议措施 = Column("AI建议措施", Text, comment="AI建议措施")
    是否已读 = Column("是否已读", Integer, default=0, comment="是否已读")

    supplier = relationship("Supplier", back_populates="risk_alerts")


class CommodityPrice(Base, TimestampMixin):
    __tablename__ = "大宗商品价格"

    商品编码 = Column("商品编码", String(50), nullable=False, comment="商品编码")
    商品名称 = Column("商品名称", String(100), nullable=False, comment="商品名称")
    当前价格 = Column("当前价格", Float, nullable=False, comment="当前价格")
    货币单位 = Column("货币单位", String(10), default="CNY", comment="货币单位")
    单位 = Column("单位", String(20), comment="单位")
    涨跌幅 = Column("涨跌幅", Float, comment="涨跌幅(%)")
    趋势 = Column("趋势", String(20), comment="趋势")


class SourcingRecommendation(Base, TimestampMixin):
    __tablename__ = "寻源推荐"

    备件ID = Column("备件ID", Integer, comment="备件ID")
    规格书内容 = Column("规格书内容", Text, comment="备件规格书内容")
    推荐供应商列表 = Column("推荐供应商列表", JSON, comment="推荐供应商列表")
