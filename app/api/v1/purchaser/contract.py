from fastapi import UploadFile, File, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_purchaser
from app.core.database import get_async_session
from app.models.purchase import Contract, Supplier
from app.services.ai_services.contract_agent import contract_agent
from app.services.contract_storage import (
    CONTRACT_MINIO_PREFIX,
    parse_contract_object_name,
    build_contract_file_body,
)
from app.utils.minio_client import minio_client
from app.config.settings import settings


class ContractReviewRequest(BaseModel):
    合同文本: str
    合同类型: str = "purchase"


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
            description="上传合同文件，AI自动审查并识别风险条款，文件存 MinIO",
            tags=["采购-合同审查"],
        )(self.review_contract_file)

        self.router.get(
            "/list",
            response_model=BaseResponse,
            summary="合同列表查询",
            description="从数据库查询合同记录，并与 MinIO 桶内文件按路径精准匹配",
            tags=["采购-合同审查"],
        )(self.list_contracts)

        self.router.get(
            "/download-url",
            response_model=BaseResponse,
            summary="获取合同下载链接",
            description="获取 MinIO 中合同文件的预签名下载 URL",
            tags=["采购-合同审查"],
        )(self.get_contract_url)

        return self.router

    async def review_contract(self, request: ContractReviewRequest, _=Depends(allow_purchaser)):
        result = await contract_agent.review_contract(
            request.合同文本, request.合同类型
        )
        return BaseResponse(data=result)

    async def review_contract_file(
        self, files: list[UploadFile] = File(...), _=Depends(allow_purchaser)
    ):
        if not files:
            return BaseResponse(code=400, msg="请至少上传一个文件")
        file = files[0]
        content = await file.read()
        object_name = f"{CONTRACT_MINIO_PREFIX}{file.filename}"

        minio_result = minio_client.put_object_exact(
            content, object_name, bucket=settings.KB_BUCKET_NAME
        )

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = f"（二进制合同文件：{file.filename}）"
        result = await contract_agent.review_contract(text)
        result["存储信息"] = minio_result
        result["对象名"] = object_name
        return BaseResponse(data=result)

    async def list_contracts(
        self,
        session: AsyncSession = Depends(get_async_session),
        _=Depends(allow_purchaser),
    ):
        """数据库合同记录 + MinIO 文件精准匹配（按文件路径对象名）"""
        result = await session.execute(
            select(Contract, Supplier.供应商名称)
            .join(Supplier, Contract.供应商ID == Supplier.id)
            .order_by(Contract.签订日期.desc())
        )
        rows = result.all()

        minio_files = minio_client.list_files(
            bucket=settings.KB_BUCKET_NAME,
            prefix=CONTRACT_MINIO_PREFIX,
        )
        minio_by_object = {f["object_name"]: f for f in minio_files}
        db_object_names: set[str] = set()

        items: list[dict] = []
        matched_count = 0
        for contract, supplier_name in rows:
            obj_name = parse_contract_object_name(contract.文件路径 or "")
            if obj_name:
                db_object_names.add(obj_name)
            mf = minio_by_object.get(obj_name) if obj_name else None
            is_matched = mf is not None
            if is_matched:
                matched_count += 1
            items.append({
                "id": contract.id,
                "合同编号": contract.合同编号,
                "合同标题": contract.合同标题 or "",
                "供应商名称": supplier_name or "",
                "签订日期": str(contract.签订日期) if contract.签订日期 else "",
                "到期日期": str(contract.到期日期) if contract.到期日期 else "",
                "AI审查状态": contract.AI审查状态 or "",
                "文件路径": contract.文件路径 or "",
                "对象名": obj_name,
                "文件已匹配": is_matched,
                "文件大小": mf["size"] if mf else 0,
                "修改时间": mf.get("last_modified", "") if mf else "",
            })

        orphan_files = [
            {
                "对象名": obj,
                "文件名": info["filename"],
                "大小": info["size"],
                "修改时间": info.get("last_modified", ""),
            }
            for obj, info in minio_by_object.items()
            if obj not in db_object_names
        ]

        payload = {
            "列表": items,
            "总数": len(items),
            "已匹配数": matched_count,
            "未匹配数": len(items) - matched_count,
            "MinIO孤立文件": orphan_files,
        }
        return BaseResponse(data=payload)

    async def get_contract_url(
        self,
        object_name: str = Query(..., description="MinIO 对象名，如 contracts/CT001.pdf"),
        _=Depends(allow_purchaser),
    ):
        url = minio_client.get_file_url(settings.KB_BUCKET_NAME, object_name)
        return BaseResponse(data={"下载链接": url, "对象名": object_name})
