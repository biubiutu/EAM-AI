class UserRole:
    ADMIN = "admin"
    ENGINEER = "engineer"
    SUPERVISOR = "supervisor"
    PURCHASER = "purchaser"
    LEADER = "leader"
    GUEST = "guest"


class EquipmentStatus:
    IN_USE = "in_use"              # 正常使用
    IN_STORAGE = "in_storage"      # 入库待使用
    PENDING_REPAIR = "pending_repair"  # 待维修
    UNDER_REPAIR = "under_repair"  # 维修中
    SCRAPPED = "scrapped"          # 已报废


class EngineerLevel:
    JUNIOR = "junior"              # 初级
    INTERMEDIATE = "intermediate"  # 中级
    SENIOR = "senior"              # 高级
    EXPERT = "expert"              # 专家


class RequisitionStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AIReviewStatus:
    PASS = "pass"
    WARNING = "warning"
    FORCE_REVIEW = "force_review"


class TransferStatus:
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RiskLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType:
    NATURAL_DISASTER = "natural_disaster"
    FIRE_ACCIDENT = "fire_accident"
    FINANCIAL_CRISIS = "financial_crisis"
    NEWS_NEGATIVE = "news_negative"
    DELIVERY_DELAY = "delivery_delay"
    QUALITY_DROP = "quality_drop"