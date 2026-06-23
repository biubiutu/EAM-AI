from fastapi import Depends
from pydantic import BaseModel, Field, AliasChoices

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_purchaser
from app.services.ai_services.supplier_risk_agent import supplier_risk_agent


class SupplierRiskRequest(BaseModel):
    supplier_id: int | str = Field(default=0, validation_alias=AliasChoices("供应商ID", "supplier_id"))
    supplier: dict = None
    supplier_name: str = Field(default="", validation_alias=AliasChoices("供应商名称", "supplier_name"))


class SupplierRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/risk-check",
            response_model=BaseResponse,
            summary="供应商风险评估",
            description="检查供应商风险等级，生成风险评估报告",
            tags=["采购-供应商管理"],
        )(self.check_risk)

        self.router.post(
            "/sourcing",
            response_model=BaseResponse,
            summary="供应商推荐",
            description="根据备件规格和供应商信息，AI推荐最优供应商方案",
            tags=["采购-供应商管理"],
        )(self.recommend_suppliers)

        self.router.post(
            "/price-trend",
            response_model=BaseResponse,
            summary="价格趋势分析",
            description="分析备件原材料价格趋势，预测未来价格走势",
            tags=["采购-供应商管理"],
        )(self.analyze_price_trend)

        return self.router

    async def check_risk(self, request: SupplierRiskRequest, _=Depends(allow_purchaser)):
        supplier = request.supplier or {
            "id": request.supplier_id,
            "name": request.supplier_name,
        }
        alerts = await supplier_risk_agent.monitor_supplier_risks(supplier)
        assessment = {}
        if alerts:
            assessment = await supplier_risk_agent.assess_risks(alerts, supplier)
        return BaseResponse(data={"alerts": alerts, "assessment": assessment})

    async def recommend_suppliers(self, request: dict, _=Depends(allow_purchaser)):
        from app.services.ai_services.sourcing_agent import sourcing_agent
        specification = request.get("specification") or request.get("spare_part_name", "")
        result = await sourcing_agent.recommend_suppliers(
            specification,
            request.get("suppliers"),
        )
        return BaseResponse(data=result)

    async def analyze_price_trend(self, request: dict, _=Depends(allow_purchaser)):
        from app.services.ai_services.price_trend_agent import price_trend_agent
        result = await price_trend_agent.analyze_price_trend(
            request.get("spare_part_id", 0),
            request.get("spare_part_name") or request.get("commodity_name") or request.get("商品名称", ""),
            request.get("raw_materials"),
            request.get("commodity_prices"),
        )
        return BaseResponse(data=result)
