from fastapi import Depends
from pydantic import BaseModel
from typing import Any

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_leader
from app.services.ai_services.text2sql_service import text2sql_service


class Text2SQLRequest(BaseModel):
    question: str
    table_schema: str = ""


class InsightRequest(BaseModel):
    question: str
    query_result: list[Any]


class DashboardRouter(BaseRouter):

    def _register_routes(self):
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

    async def text_to_sql(self, request: Text2SQLRequest, _=Depends(allow_leader)):
        result = await text2sql_service.generate_sql(request.question, request.table_schema)
        return BaseResponse(data=result)

    async def generate_insight(self, request: InsightRequest, _=Depends(allow_leader)):
        result = await text2sql_service.generate_insight(
            request.question, request.query_result
        )
        return BaseResponse(data=result)
