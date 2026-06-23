from fastapi import Depends
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import get_current_user
from app.core.database import get_async_session
from app.models.ai_feedback import AIFeedback
from app.models.golden_qa import GoldenQA
from app.services.golden_qa_service import golden_qa_service


class FeedbackSubmit(BaseModel):
    场景: str = Field(..., alias="场景")
    问题: str = Field("", alias="问题")
    AI回答: str = Field("", alias="AI回答")
    引用片段JSON: list = Field(default_factory=list, alias="引用片段JSON")
    评分: int = Field(3, ge=1, le=5, alias="评分")
    是否准确: bool = Field(True, alias="是否准确")
    工程师纠错: str = Field("", alias="工程师纠错")


class FeedbackRouter(BaseRouter):

    def _register_routes(self):
        self.router.post("/submit", response_model=BaseResponse, summary="提交AI回答评测",
                         tags=["工程师-AI评测"])(self.submit)
        self.router.get("/mine", response_model=BaseResponse, summary="我的评测记录",
                        tags=["工程师-AI评测"])(self.mine)
        self.router.get("/pending", response_model=BaseResponse, summary="待审核评测列表",
                        tags=["管理员-AI评测"])(self.pending_list)
        self.router.post("/approve", response_model=BaseResponse, summary="审核通过评测并加入黄金库",
                         tags=["管理员-AI评测"])(self.approve)
        return self.router

    async def submit(self, request: FeedbackSubmit, _=Depends(get_current_user)):
        user = _
        fb = AIFeedback(
            用户ID=user.get("用户ID"),
            场景=request.场景,
            问题=request.问题,
            AI回答=request.AI回答,
            引用片段JSON=request.引用片段JSON,
            评分=request.评分,
            是否准确=request.是否准确,
            工程师纠错=request.工程师纠错,
            状态="pending",
        )
        from app.core.database import async_session_factory
        async with async_session_factory() as session:
            session.add(fb)
            await session.commit()
            await session.refresh(fb)
        return BaseResponse(data={"id": fb.id}, msg="提交成功")

    async def mine(self, db: AsyncSession = Depends(get_async_session), _=Depends(get_current_user)):
        user = _
        result = await db.execute(
            select(AIFeedback).where(AIFeedback.用户ID == user.get("用户ID"))
            .order_by(AIFeedback.id.desc()).limit(50)
        )
        items = result.scalars().all()
        return BaseResponse(data=[{
            "id": f.id, "场景": f.场景, "问题": f.问题,
            "评分": f.评分, "是否准确": f.是否准确, "状态": f.状态,
        } for f in items])

    async def pending_list(self, db: AsyncSession = Depends(get_async_session), _=Depends(get_current_user)):
        result = await db.execute(
            select(AIFeedback).where(AIFeedback.状态 == "pending").order_by(AIFeedback.id.desc()).limit(50)
        )
        items = result.scalars().all()
        return BaseResponse(data=[{
            "id": f.id, "用户ID": f.用户ID, "场景": f.场景,
            "问题": f.问题, "AI回答": f.AI回答,
            "评分": f.评分, "是否准确": f.是否准确, "工程师纠错": f.工程师纠错,
        } for f in items])

    async def approve(self, request: dict, db: AsyncSession = Depends(get_async_session),
                      _=Depends(get_current_user)):
        feedback_id = request.get("id")
        action = request.get("action", "approve")
        result = await db.execute(select(AIFeedback).where(AIFeedback.id == feedback_id))
        fb = result.scalar_one_or_none()
        if not fb:
            return BaseResponse(code=404, msg="评测记录不存在")

        if action == "approve":
            fb.状态 = "approved"
            await db.commit()
            # 加入黄金问答库
            await golden_qa_service.add_from_feedback(
                feedback_id=fb.id,
                question=fb.问题 or "",
                answer=fb.工程师纠错 or fb.AI回答 or "",
                sources=str(fb.引用片段JSON or ""),
                scene=fb.场景,
            )
            return BaseResponse(msg="审核通过，已加入黄金问答库")
        else:
            fb.状态 = "rejected"
            await db.commit()
            return BaseResponse(msg="已驳回")


feedback_router = FeedbackRouter()