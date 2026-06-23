import random
import hashlib
from datetime import datetime, timedelta


class SupplierRiskAgent:
    # Predefined risk templates for deterministic demo data
    RISK_TEMPLATES = [
        {
            "alert_type": "delivery_delay",
            "severity": "warning",
            "title": "近期交付延迟风险",
            "content": "该供应商近3个月交付准时率下降至85%，存在产能不足或物流受阻的可能。",
            "source": "内部交付数据分析",
            "ai_suggestion": "建议增加安全库存至2周用量，并与其确认产能恢复计划。"
        },
        {
            "alert_type": "quality_issue",
            "severity": "critical",
            "title": "质量抽检不合格率上升",
            "content": "最近两批次到货抽检不合格率达到8%，主要问题为尺寸公差超标。",
            "source": "质量管理部门抽检报告",
            "ai_suggestion": "立即启动供应商质量整改程序，暂停新订单下达，要求提交8D报告。"
        },
        {
            "alert_type": "financial_risk",
            "severity": "warning",
            "title": "财务状况异常信号",
            "content": "公开信息显示该供应商近期存在多起合同纠纷及被执行记录，现金流可能承压。",
            "source": "企业征信数据监测",
            "ai_suggestion": "建议缩短账期或要求预付款比例提升至30%，同时开发备选供应商。"
        },
        {
            "alert_type": "price_volatility",
            "severity": "info",
            "title": "原材料价格波动影响",
            "content": "该供应商主营品类关联的铜材价格近30天上涨12%，存在调价风险。",
            "source": "大宗商品价格监测",
            "ai_suggestion": "建议锁定未来3个月采购价格，或签订价格联动条款合同。"
        },
        {
            "alert_type": "single_source",
            "severity": "warning",
            "title": "单一供应源依赖风险",
            "content": "该备件目前仅由此供应商独家供应，一旦断供将直接导致产线停产。",
            "source": "供应结构分析",
            "ai_suggestion": "建议启动二供开发计划，目标6个月内完成样品认证并小批量试产。"
        },
        {
            "alert_type": "credit_downgrade",
            "severity": "critical",
            "title": "信用评级下调预警",
            "content": "第三方信用评级机构近期将该供应商评级从AA下调至BBB，偿债能力存疑。",
            "source": "信用评级机构公告",
            "ai_suggestion": "建议冻结新增授信额度，存量应收账款加速回收，启动法律保全措施。"
        },
        {
            "alert_type": "regulatory",
            "severity": "warning",
            "title": "环保合规风险",
            "content": "该供应商所在地区环保督查趋严，其电镀工序存在排放超标记录，可能面临限产。",
            "source": "环保部门公开信息",
            "ai_suggestion": "建议要求供应商提交环保整改方案及时间表，同时评估替代电镀工艺供应商。"
        },
        {
            "alert_type": "geo_political",
            "severity": "info",
            "title": "地缘政治运输风险",
            "content": "供应商位于边境贸易区，近期口岸通关时效延长，平均运输时间增加3-5天。",
            "source": "物流运输监测",
            "ai_suggestion": "建议调整采购提前期，或考虑通过内陆渠道分流部分订单。"
        },
    ]

    def _get_seed(self, supplier: dict) -> int:
        name = supplier.get("name", "") or supplier.get("供应商名称", "")
        return int(hashlib.md5(name.encode()).hexdigest(), 16)

    def _generate_demo_alerts(self, supplier: dict) -> list:
        seed = self._get_seed(supplier)
        rng = random.Random(seed)
        count = rng.randint(1, 4)
        alerts = []
        indices = rng.sample(range(len(self.RISK_TEMPLATES)), count)
        for idx in indices:
            alert = self.RISK_TEMPLATES[idx].copy()
            days_ago = rng.randint(1, 30)
            alert["detected_at"] = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            alerts.append(alert)
        return alerts

    def _generate_demo_assessment(self, alerts: list, supplier: dict) -> dict:
        seed = self._get_seed(supplier)
        rng = random.Random(seed + 999)
        severities = [a["severity"] for a in alerts]
        if "critical" in severities:
            level = "high"
            should_backup = True
        elif "warning" in severities:
            level = "medium"
            should_backup = rng.choice([True, False])
        else:
            level = "low"
            should_backup = False
        measures = []
        suggestions = []
        for a in alerts:
            if a.get("ai_suggestion"):
                if a["severity"] == "critical":
                    measures.append(a["ai_suggestion"])
                else:
                    suggestions.append(a["ai_suggestion"])
        if not measures:
            measures = ["保持常规监控频率"]
        if not suggestions:
            suggestions = ["每月复核供应商KPI指标"]
        return {
            "overall_risk_level": level,
            "should_activate_backup": should_backup,
            "emergency_measures": measures[:3],
            "monitoring_suggestions": suggestions[:3],
            "summary": f"综合评估：该供应商当前风险等级为【{level}】，共识别{len(alerts)}项风险点。"
        }

    async def monitor_supplier_risks(self, supplier: dict) -> list:
        return self._generate_demo_alerts(supplier)

    async def assess_risks(self, alerts: list, supplier: dict) -> dict:
        return self._generate_demo_assessment(alerts, supplier)


supplier_risk_agent = SupplierRiskAgent()
