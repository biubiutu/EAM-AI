from fastapi import UploadFile, File, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json
import os
import shutil
import tempfile
from datetime import datetime

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_purchaser
from app.core.database import get_async_session
from app.models.purchase import Quotation, PriceComparison, Supplier
from app.services.ai_services.quotation_agent import quotation_agent
from app.utils.ai_client import ai_client
from app.utils.minio_client import minio_client
from app.config.settings import settings

LIST_LIMIT = 50
DEFAULT_SUPPLIER_ID = 1


def _extract_json(text: str) -> str:
    import re
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r'```\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def _normalize_quotation_item(item: dict) -> dict:
    return {
        "supplier": item.get("supplier") or item.get("供应商") or "",
        "spare_part_name": item.get("spare_part_name") or item.get("备件名称") or "",
        "specification": item.get("specification") or item.get("规格型号") or "",
        "unit_price": item.get("unit_price") if item.get("unit_price") is not None else item.get("单价"),
        "quantity": item.get("quantity") if item.get("quantity") is not None else item.get("数量"),
        "total_price": item.get("total_price") if item.get("total_price") is not None else item.get("总价"),
        "currency": item.get("currency") or item.get("币种") or "CNY",
        "delivery_days": item.get("delivery_days") if item.get("delivery_days") is not None else item.get("交期天数"),
        "payment_terms": item.get("payment_terms") or item.get("付款条件") or "",
        "valid_until": item.get("valid_until") or item.get("有效期") or "",
        "tax_included": item.get("tax_included") if item.get("tax_included") is not None else item.get("含税"),
    }


def _item_to_chinese(item: dict) -> dict:
    n = _normalize_quotation_item(item)
    return {
        "备件名称": n["spare_part_name"] or "-",
        "规格型号": n["specification"] or "-",
        "单价": n["unit_price"],
        "数量": n["quantity"],
        "总价": n["total_price"],
        "币种": n["currency"],
        "交期天数": n["delivery_days"],
        "付款条件": n["payment_terms"] or "-",
        "有效期": n["valid_until"] or "-",
        "含税": "是" if n["tax_included"] is True else ("否" if n["tax_included"] is False else "-"),
    }


def _compare_to_chinese(result: dict, spare_part_name: str = "") -> dict:
    summary = []
    for row in result.get("summary_table") or []:
        summary.append({
            "供应商ID": row.get("supplier_id"),
            "供应商名称": row.get("supplier_name") or row.get("supplier") or "-",
            "单价": row.get("unit_price"),
            "交期天数": row.get("delivery_days"),
            "付款条件": row.get("payment_terms") or "-",
            "综合得分": row.get("total_score"),
        })
    dim = result.get("dimension_scores") or {}
    dim_cn = {}
    dim_labels = {
        "price": "价格", "delivery": "交期",
        "payment_terms": "付款条件", "quality_history": "质量历史",
    }
    for key, label in dim_labels.items():
        if key in dim:
            dim_cn[label] = dim[key]
    return {
        "备件名称": spare_part_name,
        "推荐供应商ID": result.get("recommended_supplier_id"),
        "推荐理由": result.get("reason") or "",
        "维度评分": dim_cn,
        "汇总表": summary,
        "谈判建议": result.get("negotiation_suggestions") or [],
    }


class CompareRequest(BaseModel):
    备件名称: str = ""
    报价列表: list[dict] = Field(default_factory=list)


class QuotationRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/upload",
            response_model=BaseResponse,
            summary="上传报价单(多文件)",
            description="上传多个报价单文件(PDF/Excel/图片)，AI自动提取报价信息，文件存 MinIO",
            tags=["采购-询价比价"],
        )(self.upload_quotations)

        self.router.post(
            "/compare",
            response_model=BaseResponse,
            summary="比价分析",
            description="对比多个供应商的报价，生成比价分析报告和推荐方案",
            tags=["采购-询价比价"],
        )(self.compare_quotations)

        self.router.get(
            "/list",
            response_model=BaseResponse,
            summary="报价单列表",
            tags=["采购-询价比价"],
        )(self.list_quotations)

        self.router.get(
            "/comparisons",
            response_model=BaseResponse,
            summary="比价记录列表",
            tags=["采购-询价比价"],
        )(self.list_comparisons)

        return self.router

    async def upload_quotations(
        self,
        files: list[UploadFile] = File(...),
        session: AsyncSession = Depends(get_async_session),
        _=Depends(allow_purchaser),
    ):
        results = []
        for file in files:
            result = await self._process_single_quotation(file, session)
            results.append(result)
        return BaseResponse(data=results)

    async def _save_quotation_record(
        self,
        session: AsyncSession,
        filename: str,
        items: list,
        storage: dict,
        ocr_confidence: float | None = None,
    ) -> None:
        if not items:
            return
        supplier_id = DEFAULT_SUPPLIER_ID
        supplier = await session.get(Supplier, supplier_id)
        if not supplier:
            first = await session.execute(select(Supplier.id).limit(1))
            sid = first.scalar_one_or_none()
            if not sid:
                return
            supplier_id = sid
        quotation_no = f"Q-{datetime.now().strftime('%Y%m%d%H%M%S')}-{filename[:20]}"
        record = Quotation(
            报价单号=quotation_no,
            供应商ID=supplier_id,
            报价明细=items,
            原始文件路径=storage.get("url") or storage.get("path") or filename,
            OCR状态="success",
            OCR置信度=ocr_confidence,
            报价状态="received",
        )
        session.add(record)
        await session.commit()

    async def _process_single_quotation(self, file: UploadFile, session: AsyncSession) -> dict:
        content = await file.read()

        minio_result = minio_client.upload_file(
            content, file.filename,
            bucket=settings.KB_BUCKET_NAME,
            prefix="quotations/",
        )

        ext = os.path.splitext(file.filename)[1].lower()
        image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}
        item: dict = {"文件名": file.filename, "存储信息": minio_result}

        try:
            if ext == ".pdf":
                tmp_dir = tempfile.mkdtemp()
                tmp = os.path.join(tmp_dir, file.filename)
                try:
                    with open(tmp, "wb") as f:
                        f.write(content)
                    text = quotation_agent.extract_pdf_text(tmp)
                    ai_result = await quotation_agent.extract_from_text(text)
                    raw_items = ai_result if isinstance(ai_result, list) else ai_result.get("items", [])
                    item["报价明细"] = [_item_to_chinese(i) for i in raw_items]
                    item["备注"] = "PDF 解析成功"
                finally:
                    shutil.rmtree(tmp_dir, ignore_errors=True)

            elif ext in [".xlsx", ".xls"]:
                tmp_dir = tempfile.mkdtemp()
                tmp = os.path.join(tmp_dir, file.filename)
                try:
                    with open(tmp, "wb") as f:
                        f.write(content)
                    text = quotation_agent.extract_excel_text(tmp)
                    ai_result = await quotation_agent.extract_from_text(text)
                    raw_items = ai_result if isinstance(ai_result, list) else ai_result.get("items", [])
                    item["报价明细"] = [_item_to_chinese(i) for i in raw_items]
                    item["备注"] = "Excel 解析成功"
                finally:
                    shutil.rmtree(tmp_dir, ignore_errors=True)

            elif ext in image_exts:
                prompt = """请识别这张报价单图片中的所有文字信息，以JSON格式输出（数组，支持多行报价）：
[
    {
        "spare_part_name": "备件名称",
        "specification": "规格型号",
        "unit_price": 45.00,
        "quantity": 100,
        "total_price": 4500.00,
        "currency": "CNY",
        "delivery_days": 7,
        "payment_terms": "月结30天",
        "valid_until": "2024-12-31",
        "tax_included": true
    }
]"""
                text = await ai_client.chat_with_image(
                    prompt, content, mime_type=ai_client.get_image_mime_type(file.filename)
                )
                try:
                    parsed = json.loads(_extract_json(text))
                    raw_items = parsed if isinstance(parsed, list) else parsed.get("items", [])
                    item["报价明细"] = [_item_to_chinese(i) for i in raw_items]
                    item["备注"] = f"图片识别成功，提取到 {len(item['报价明细'])} 条报价"
                except json.JSONDecodeError:
                    item["报价明细"] = []
                    item["原始文本"] = text
                    item["备注"] = "图片已识别但未能解析为结构化数据，可查看原始文本"
                item["是否图片"] = True

            else:
                text = content.decode("utf-8", errors="replace")
                ai_result = await quotation_agent.extract_from_text(text)
                raw_items = ai_result if isinstance(ai_result, list) else ai_result.get("items", [])
                item["报价明细"] = [_item_to_chinese(i) for i in raw_items]
                item["备注"] = "文本解析成功"

        except Exception as e:
            item["报价明细"] = []
            item["备注"] = f"解析失败: {str(e)}"

        if item.get("报价明细"):
            try:
                await self._save_quotation_record(
                    session, file.filename, item["报价明细"], minio_result
                )
            except Exception as e:
                item["备注"] = f"{item.get('备注', '')}（落库失败: {e}）"

        return item

    async def compare_quotations(
        self,
        request: CompareRequest,
        session: AsyncSession = Depends(get_async_session),
        user=Depends(allow_purchaser),
    ):
        if not request.报价列表:
            return BaseResponse(code=400, msg="请提供至少一条报价数据")

        normalized = [_normalize_quotation_item(q) for q in request.报价列表]
        try:
            result = await quotation_agent.compare_quotations(normalized)
        except Exception as e:
            return BaseResponse(code=500, msg=f"比价分析失败: {e}")

        chinese = _compare_to_chinese(result, request.备件名称)
        comparison_no = f"PC-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        record = PriceComparison(
            比价单号=comparison_no,
            备件ID=None,
            参与比价报价单ID列表=[],
            比价结果=chinese,
            创建人ID=user.get("用户ID"),
        )
        session.add(record)
        await session.commit()

        return BaseResponse(data=chinese)

    async def list_quotations(
        self,
        session: AsyncSession = Depends(get_async_session),
        _=Depends(allow_purchaser),
    ):
        result = await session.execute(
            select(Quotation, Supplier)
            .join(Supplier, Quotation.供应商ID == Supplier.id)
            .order_by(Quotation.id.desc())
            .limit(LIST_LIMIT)
        )
        rows = []
        for q, s in result.all():
            items = q.报价明细 or []
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except json.JSONDecodeError:
                    items = []
            rows.append({
                "报价单号": q.报价单号,
                "供应商名称": s.供应商名称,
                "报价明细": items,
                "OCR状态": q.OCR状态,
                "OCR置信度": q.OCR置信度,
                "状态": q.报价状态,
                "创建时间": q.created_at.strftime("%Y-%m-%d %H:%M") if q.created_at else "-",
            })
        return BaseResponse(data=rows)

    async def list_comparisons(
        self,
        session: AsyncSession = Depends(get_async_session),
        _=Depends(allow_purchaser),
    ):
        result = await session.execute(
            select(PriceComparison).order_by(PriceComparison.id.desc()).limit(LIST_LIMIT)
        )
        rows = []
        for c in result.scalars().all():
            cr = c.比价结果 or {}
            rows.append({
                "比价单号": c.比价单号,
                "备件名称": cr.get("备件名称") or "-",
                "推荐供应商ID": cr.get("推荐供应商ID"),
                "推荐理由": cr.get("推荐理由") or "-",
                "汇总表": cr.get("汇总表") or [],
                "谈判建议": cr.get("谈判建议") or [],
                "创建时间": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else "-",
            })
        return BaseResponse(data=rows)
