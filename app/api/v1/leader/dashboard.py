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
from app.models.purchase import Supplier
from app.models.spare_part import Requisition
from app.services.text2sql_service import text2sql_service
from app.utils.ai_client import ai_client


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
            description="获取实时业务关键指标数据",
            tags=["领导-数据看板"],
        )(self.dashboard_metrics)

        self.router.post(
            "/query",
            response_model=BaseResponse,
            summary="Text2SQL真实数据查询",
            description="将自然语言问题转换为SQL查询，自动从数据库获取业务数据（真实数据，不再使用mock）",
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
                "审批单号": r.审批单号 or str(r.id),
                "类型": r.业务类型 or "-",
                "申请人ID": r.申请人ID,
                "状态": r.审批状态 or "pending",
                "AI摘要": r.AI审批摘要 or "-",
                "创建时间": str(r.created_at)[:19] if r.created_at else "-",
            })
        return BaseResponse(data=data)

    async def approval_action(self, request: ApprovalActionRequest,
                              session: AsyncSession = Depends(get_async_session),
                              _=Depends(allow_leader)):
        # 实际更新审批状态
        result = await session.execute(
            select(ApprovalRecord).where(ApprovalRecord.审批单号 == request.审批ID)
        )
        record = result.scalar_one_or_none()
        if record:
            record.审批状态 = "approved" if request.操作 == "approve" else "rejected"
            record.AI审批摘要 = request.意见 or record.AI审批摘要
            await session.commit()
        action_text = "同意" if request.操作 == "approve" else "拒绝"
        return BaseResponse(data={"消息": f"审批事项 {request.审批ID} 已{action_text}", "操作": request.操作})

    async def dashboard_metrics(self, session: AsyncSession = Depends(get_async_session),
                                _=Depends(allow_leader)):
        eq_count = (await session.execute(select(func.count(Equipment.id)))).scalar() or 0
        wo_count = (await session.execute(select(func.count(WorkOrder.id)))).scalar() or 0
        req_count = (await session.execute(select(func.count(Requisition.id)))).scalar() or 0
        supplier_count = (await session.execute(select(func.count(Supplier.id)))).scalar() or 0
        data = [
            {"名称": "设备总数", "数值": str(eq_count)},
            {"名称": "本月维修单", "数值": str(wo_count)},
            {"名称": "申购单数", "数值": str(req_count)},
            {"名称": "供应商数", "数值": str(supplier_count)},
        ]
        return BaseResponse(data=data)

    async def text_to_sql(self, request: Text2SQLRequest, _=Depends(allow_leader)):
        result = await text2sql_service.query(request.问题)
        return BaseResponse(data=result)

    async def generate_insight(self, request: InsightRequest, _=Depends(allow_leader)):
        prompt = f"""你是数据分析专家。请根据用户问题和查询结果生成深刻洞察。

【用户问题】
{request.问题}

【查询结果】
{request.查询结果[:50]}

请给出：
1. 数据概况
2. 关键发现
3. 建议措施（如适用）
"""
        answer = await ai_client.chat(prompt)
        return BaseResponse(data={"answer": answer})
