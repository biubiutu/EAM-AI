from fastapi import UploadFile, File, Depends
from pydantic import BaseModel

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_purchaser
from app.services.ai_services.quotation_agent import quotation_agent
import aiofiles
import os
import tempfile


class CompareRequest(BaseModel):
    quotations: list[dict]


class QuotationRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/upload",
            response_model=BaseResponse,
            summary="上传报价单",
            description="上传PDF/Excel报价单文件，AI自动提取报价信息",
            tags=["采购-询价比价"],
        )(self.upload_quotation)

        self.router.post(
            "/compare",
            response_model=BaseResponse,
            summary="比价分析",
            description="对比多个供应商的报价，生成比价分析报告和推荐方案",
            tags=["采购-询价比价"],
        )(self.compare_quotations)

        return self.router

    async def upload_quotation(self, file: UploadFile = File(...), _=Depends(allow_purchaser)):
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        ext = os.path.splitext(file.filename)[1].lower()
        if ext == ".pdf":
            text = quotation_agent.extract_pdf_text(file_path)
        elif ext in [".xlsx", ".xls"]:
            text = quotation_agent.extract_excel_text(file_path)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

        result = await quotation_agent.extract_from_text(text)
        return BaseResponse(data=result)

    async def compare_quotations(self, request: CompareRequest, _=Depends(allow_purchaser)):
        result = await quotation_agent.compare_quotations(request.quotations)
        return BaseResponse(data=result)
