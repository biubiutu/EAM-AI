from fastapi import Depends
from pydantic import BaseModel

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_supervisor
from app.services.audit_service import audit_service
from app.services.golden_qa_service import golden_qa_service


class AdminRouter(BaseRouter):

    def _register_routes(self):
        self.router.get("/audit-logs", response_model=BaseResponse, summary="审计日志",
                        tags=["管理员-审计"])(self.list_audit_logs)
        self.router.get("/golden-qa", response_model=BaseResponse, summary="黄金问答列表",
                        tags=["管理员-黄金问答"])(self.list_golden_qa)
        self.router.post("/golden-qa/refresh", response_model=BaseResponse, summary="刷新黄金问答缓存",
                         tags=["管理员-黄金问答"])(self.refresh_golden_qa)
        return self.router

    async def list_audit_logs(self, page: int = 1, page_size: int = 50,
                               action_type: str = "", _=Depends(allow_supervisor)):
        result = await audit_service.get_logs(page=page, page_size=page_size, action_type=action_type)
        return BaseResponse(data=result)

    async def list_golden_qa(self, scene: str = "", page: int = 1, page_size: int = 20,
                              _=Depends(allow_supervisor)):
        result = await golden_qa_service.list_all(scene=scene, page=page, page_size=page_size)
        return BaseResponse(data=result)

    async def refresh_golden_qa(self, _=Depends(allow_supervisor)):
        await golden_qa_service._async_sync_to_minio()
        return BaseResponse(msg="黄金问答缓存已刷新")


admin_router = AdminRouter()