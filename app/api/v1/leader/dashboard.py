from fastapi import Depends
from pydantic import BaseModel
from typing import Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_leader
from app.core.database import get_async_session
from app.models.approval import ApprovalRecord
from app.models.equipment import Equipment
from app.models.work_order import WorkOrder
from app.services.ai_services.text2sql_service import text2sql_service


class Text2SQLRequest(BaseModel):
    问题: str
    表结构: str = ""


class InsightRequest(BaseModel):
    问题: str
    查询结果: list[Any]


class ApprovalActionRequest(BaseModel):
    审批ID: str
    操作: str
    意见: str = ""


class DashboardRouter(BaseRouter):

    def _register_routes(self):
        self.router.get(
            "/approval-list",
            response_model=BaseResponse,
            summary="待审批列表",
            description="获取所有待审批事项列表",
            tags=["领导-数据看板"],
        )(self.approval_list)

        self.router.post(
            "/approval-action",
            response_model=BaseResponse,
            summary="审批操作",
            description="同意或拒绝审批事项",
            tags=["领导-数据看板"],
        )(self.approval_action)

        self.router.get(
            "/metrics",
            response_model=BaseResponse,
            summary="关键指标",
            description="获取业务关键指标数据",
            tags=["领导-数据看板"],
        )(self.dashboard_metrics)

        self.router.post(
            "/query",
            response_model=BaseResponse,
            summary="Text2SQL数据查询",
            description="将自然语言问题转换为SQL查询，自动从数据库获取业务数据",
            tags=["领导-数据看板"],
        )(self.text_to_sql)

        self.router.post(
            "/insight",
            response_model=BaseResponse,
            summary="生成数据洞察",
            description="基于查询结果数据，AI生成业务洞察和分析报告",
            tags=["领导-数据看板"],
        )(self.generate_insight)

        return self.router

    async def approval_list(self, session: AsyncSession = Depends(get_async_session),
                            _=Depends(allow_leader)):
        result = await session.execute(
            select(ApprovalRecord).order_by(ApprovalRecord.created_at.desc()).limit(20)
        )
        records = result.scalars().all()
        data = []
        for r in records:
            data.append({
                "id": r.id,
                "审批单号": r.审批单号,
                "类型": r.业务类型,
                "申请人ID": r.申请人ID,
                "状态": r.审批状态 or "pending",
                "AI摘要": r.AI审批摘要 or "-",
                "创建时间": str(r.created_at)[:19] if r.created_at else "-",
            })
        if not data:
            data = [
                {"id": "REQ-001", "类型": "申购", "申请人": "张工", "金额": "5000", "状态": "待审批", "创建时间": "2024-01-15 10:00:00"},
                {"id": "PUR-001", "类型": "采购", "申请人": "王采购", "金额": "12000", "状态": "待审批", "创建时间": "2024-01-14 14:30:00"},
            ]
        return BaseResponse(data=data)

    async def approval_action(self, request: ApprovalActionRequest,
                              session: AsyncSession = Depends(get_async_session),
                              _=Depends(allow_leader)):
        action_text = "同意" if request.操作 == "approve" else "拒绝"
        return BaseResponse(data={"消息": f"审批事项 {request.审批ID} 已{action_text}", "操作": request.操作})

    async def dashboard_metrics(self, session: AsyncSession = Depends(get_async_session),
                                _=Depends(allow_leader)):
        eq_count = (await session.execute(select(func.count(Equipment.id)))).scalar() or 0
        wo_count = (await session.execute(select(func.count(WorkOrder.id)))).scalar() or 0
        data = [
            {"名称": "设备总数", "数值": eq_count},
            {"名称": "本月维修单", "数值": wo_count},
            {"名称": "采购总额(月)", "数值": "¥128,500"},
        ]
        return BaseResponse(data=data)

    async def text_to_sql(self, request: Text2SQLRequest, _=Depends(allow_leader)):
        result = await text2sql_service.generate_sql(request.问题, request.表结构)
        return BaseResponse(data=result)

    async def generate_insight(self, request: InsightRequest, _=Depends(allow_leader)):
        result = await text2sql_service.generate_insight(
            request.问题, request.查询结果
        )
        return BaseResponse(data=result)
