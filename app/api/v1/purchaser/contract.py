from fastapi import UploadFile, File, Depends
from pydantic import BaseModel

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_purchaser
from app.services.ai_services.contract_agent import contract_agent


class ContractReviewRequest(BaseModel):
    contract_text: str
    contract_type: str = "purchase"


class ContractRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/review",
            response_model=BaseResponse,
            summary="合同文本审查",
            description="AI审查合同文本内容，识别风险条款并给出修改建议",
            tags=["采购-合同审查"],
        )(self.review_contract)

        self.router.post(
            "/review-file",
            response_model=BaseResponse,
            summary="合同文件审查",
            description="上传合同文件，AI自动审查并识别风险条款",
            tags=["采购-合同审查"],
        )(self.review_contract_file)

        return self.router

    async def review_contract(self, request: ContractReviewRequest, _=Depends(allow_purchaser)):
        result = await contract_agent.review_contract(
            request.contract_text, request.contract_type
        )
        return BaseResponse(data=result)

    async def review_contract_file(self, file: UploadFile = File(...), _=Depends(allow_purchaser)):
        content = await file.read()
        text = content.decode("utf-8")
        result = await contract_agent.review_contract(text)
        return BaseResponse(data=result)
