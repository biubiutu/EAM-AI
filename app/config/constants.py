class UserRole:
    ADMIN = "admin"
    ENGINEER = "engineer"
    SUPERVISOR = "supervisor"
    PURCHASER = "purchaser"
    LEADER = "leader"
    GUEST = "guest"


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