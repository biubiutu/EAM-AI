from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON, Date
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"

    code = Column(String(50), unique=True, nullable=False, comment="供应商编码")
    name = Column(String(200), nullable=False, comment="供应商名称")
    contact_person = Column(String(100), comment="联系人")
    contact_phone = Column(String(50), comment="联系电话")
    email = Column(String(100), comment="邮箱")
    address = Column(String(500), comment="地址")
    delivery_on_time_rate = Column(Float, comment="历史交付准时率(%)")
    quality_pass_rate = Column(Float, comment="质量合格率(%)")
    comprehensive_score = Column(Float, comment="综合推荐指数(0-100)")
    risk_level = Column(String(20), default="low", comment="风险等级: low/medium/high/critical")
    risk_tags = Column(JSON, comment="风险标签列表")
    last_risk_check = Column(DateTime, comment="最后风险检查时间")

    quotations = relationship("Quotation", back_populates="supplier")
    contracts = relationship("Contract", back_populates="supplier")
    supply_categories = relationship("SupplierCategory", back_populates="supplier")
    risk_alerts = relationship("SupplierRiskAlert", back_populates="supplier")


class SupplierCategory(Base, TimestampMixin):
    __tablename__ = "supplier_categories"

    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID")
    category = Column(String(100), nullable=False, comment="供应品类")
    is_qualified = Column(Integer, default=1, comment="是否合格供应商")

    supplier = relationship("Supplier", back_populates="supply_categories")


class Quotation(Base, TimestampMixin):
    __tablename__ = "quotations"

    quotation_no = Column(String(50), unique=True, nullable=False, comment="报价单号")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID")
    purchase_request_id = Column(Integer, comment="关联采购申请ID")
    items = Column(JSON, comment="报价明细")
    raw_file_path = Column(String(500), comment="原始报价单文件路径")
    ocr_status = Column(String(20), default="pending", comment="OCR状态: pending/success/failed")
    ocr_confidence = Column(Float, comment="OCR置信度")
    status = Column(String(20), default="received", comment="状态")

    supplier = relationship("Supplier", back_populates="quotations")


class PriceComparison(Base, TimestampMixin):
    __tablename__ = "price_comparisons"

    comparison_no = Column(String(50), unique=True, nullable=False, comment="比价单号")
    spare_part_id = Column(Integer, comment="备件ID")
    quotation_ids = Column(JSON, comment="参与比价的报价单ID列表")
    comparison_result = Column(JSON, comment="比价结果")
    created_by = Column(Integer, comment="创建人ID")


class Contract(Base, TimestampMixin):
    __tablename__ = "contracts"

    contract_no = Column(String(50), unique=True, nullable=False, comment="合同编号")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID")
    title = Column(String(300), comment="合同标题")
    file_path = Column(String(500), comment="合同文件路径")
    ai_review_status = Column(String(20), default="pending", comment="AI审查状态")
    ai_review_result = Column(JSON, comment="AI审查结果")
    signed_at = Column(Date, comment="签订日期")
    expiry_date = Column(Date, comment="到期日期")

    supplier = relationship("Supplier", back_populates="contracts")


class SupplierRiskAlert(Base, TimestampMixin):
    __tablename__ = "supplier_risk_alerts"

    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID")
    alert_type = Column(String(50), comment="预警类型")
    severity = Column(String(20), comment="严重程度: info/warning/critical")
    title = Column(String(300), comment="预警标题")
    content = Column(Text, comment="预警详情")
    source = Column(String(500), comment="信息来源")
    ai_suggestion = Column(Text, comment="AI建议措施")
    is_read = Column(Integer, default=0, comment="是否已读")

    supplier = relationship("Supplier", back_populates="risk_alerts")


class CommodityPrice(Base, TimestampMixin):
    __tablename__ = "commodity_prices"

    commodity_code = Column(String(50), nullable=False, comment="商品编码: CU/AL/STEEL/PLASTIC")
    commodity_name = Column(String(100), nullable=False, comment="商品名称")
    price = Column(Float, nullable=False, comment="当前价格")
    currency = Column(String(10), default="CNY", comment="货币单位")
    unit = Column(String(20), comment="单位")
    change_percent = Column(Float, comment="涨跌幅(%)")
    trend = Column(String(20), comment="趋势: up/down/stable")


class SourcingRecommendation(Base, TimestampMixin):
    __tablename__ = "sourcing_recommendations"

    spare_part_id = Column(Integer, comment="备件ID")
    specification = Column(Text, comment="备件规格书内容")
    recommendations = Column(JSON, comment="推荐供应商列表")