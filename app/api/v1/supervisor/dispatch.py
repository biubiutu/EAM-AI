from fastapi import Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_supervisor
from app.core.database import get_async_session
from app.models.dispatch import EngineerDispatch
from app.models.user import User
from app.utils.ai_client import ai_client

_SKILL_WEIGHT = 0.4
_DISTANCE_WEIGHT = 0.6
_DEFAULT_DISTANCE = 999.0


class DispatchCreateRequest(BaseModel):
    工程师ID: int
    工程师姓名: str
    维修地点: str
    距离公里: float = 0
    任务描述: str = ""
    工程师技能: dict = Field(default_factory=dict)


class DispatchRecommendRequest(BaseModel):
    维修地点: str
    任务描述: str = ""
    工程师列表: list[dict] = Field(default_factory=list)


class DispatchCostEstimateRequest(BaseModel):
    维修地点: str
    工程师姓名: str = ""


def _dispatch_to_dict(record: EngineerDispatch) -> dict:
    return {
        "id": record.id,
        "工程师ID": record.工程师ID,
        "工程师姓名": record.工程师姓名,
        "维修地点": record.维修地点,
        "距离公里": record.距离公里,
        "任务描述": record.任务描述,
        "状态": record.调派状态,
        "主管姓名": record.主管姓名,
        "创建时间": str(record.created_at),
        "更新时间": str(record.updated_at),
    }


class DispatchRouter(BaseRouter):

    def _register_routes(self):
        self.router.post("/create", response_model=BaseResponse, summary="创建调派记录",
                         tags=["主管-工程师调派"])(self.create_dispatch)
        self.router.get("/list", response_model=BaseResponse, summary="调派记录列表",
                        tags=["主管-工程师调派"])(self.list_dispatches)
        self.router.get("/engineers", response_model=BaseResponse, summary="获取所有工程师",
                        tags=["主管-工程师调派"])(self.list_engineers)
        self.router.post("/recommend", response_model=BaseResponse, summary="AI推荐工程师",
                         tags=["主管-工程师调派"])(self.recommend_engineers)
        self.router.post("/cost-estimate", response_model=BaseResponse, summary="AI估算调派成本与距离",
                         tags=["主管-工程师调派"])(self.estimate_cost)
        self.router.post("/complete/{dispatch_id}", response_model=BaseResponse, summary="完成调派",
                         tags=["主管-工程师调派"])(self.complete_dispatch)
        return self.router

    async def create_dispatch(
        self,
        request: DispatchCreateRequest,
        session: AsyncSession = Depends(get_async_session),
        current_user: dict = Depends(allow_supervisor),
    ):
        dispatch = EngineerDispatch(
            工程师ID=request.工程师ID,
            工程师姓名=request.工程师姓名,
            维修地点=request.维修地点,
            距离公里=request.距离公里,
            任务描述=request.任务描述,
            工程师技能=json.dumps(request.工程师技能, ensure_ascii=False),
            主管ID=current_user.get("用户ID"),
            主管姓名=current_user.get("用户名", ""),
            调派状态="dispatched",
        )
        session.add(dispatch)
        await session.commit()
        await session.refresh(dispatch)
        data = _dispatch_to_dict(dispatch)
        data["消息"] = "调派成功"
        return BaseResponse(data=data)

    async def list_dispatches(
        self,
        session: AsyncSession = Depends(get_async_session),
        _=Depends(allow_supervisor),
    ):
        result = await session.execute(
            select(EngineerDispatch).order_by(EngineerDispatch.created_at.desc())
        )
        return BaseResponse(data=[_dispatch_to_dict(r) for r in result.scalars().all()])

    async def list_engineers(
        self,
        session: AsyncSession = Depends(get_async_session),
        _=Depends(allow_supervisor),
    ):
        result = await session.execute(
            select(User).where(User.角色 == "engineer").where(User.是否激活 == True)
        )
        data = [
            {
                "id": e.id,
                "用户名": e.用户名,
                "真实姓名": e.真实姓名 or e.用户名,
                "手机号": e.手机号 or "",
            }
            for e in result.scalars().all()
        ]
        return BaseResponse(data=data)

    async def recommend_engineers(self, request: DispatchRecommendRequest, _=Depends(allow_supervisor)):
        engineers = request.工程师列表
        if not engineers:
            return BaseResponse(data={"推荐列表": [], "消息": "无可用工程师"})

        scored = []
        for eng in engineers:
            skills = eng.get("skills", eng.get("技能", {}))
            avg_skill = sum(skills.values()) / len(skills) if skills else 0
            dist = eng.get("distance", eng.get("距离", _DEFAULT_DISTANCE))
            score = avg_skill * _SKILL_WEIGHT - dist * _DISTANCE_WEIGHT
            scored.append({**eng, "技能均分": round(avg_skill, 1), "评分": round(score, 1)})

        scored.sort(key=lambda x: x["评分"], reverse=True)
        return BaseResponse(data={
            "推荐列表": scored,
            "消息": f"根据技能和距离综合评分推荐，共{len(scored)}名可用工程师",
        })

    async def estimate_cost(self, request: DispatchCostEstimateRequest, _=Depends(allow_supervisor)):
        location = request.维修地点
        engineer_name = request.工程师姓名 or "未指定工程师"

        prompt = f"""你是一个设备维修调派成本估算专家。请根据以下信息估算工程师调派的成本和距离。

【工程师】{engineer_name}
【维修地点】{location}

请根据以下规则估算：
1. 基于维修地点的描述，合理估算距离（假设公司总部在市中心）
2. 交通费用包括：出租车/网约车费用和高铁费用（起步价+每公里费用）
3. 考虑时间段因素：如果是"晚上"、"郊区"、"偏远"等关键词，费用适当上浮
4. 如地点含"公里"或"km"数字，直接使用该数字作为参考距离

以JSON格式输出：
{{
    "distance": 12.5,
    "transport_cost": 45.0,
    "other_costs": "",
    "total_cost": 45.0,
    "notes": "估算说明"
}}

注意：只返回JSON，不要其他文字。"""

        result = await ai_client.chat_with_json(prompt)
        distance = float(result.get("distance", 0))
        transport_cost = float(result.get("transport_cost", 0))
        other_costs = result.get("other_costs", "")
        total_cost = float(result.get("total_cost", transport_cost))
        notes = result.get("notes", "")

        return BaseResponse(data={
            "距离公里": round(distance, 1),
            "交通费用": round(transport_cost, 2),
            "其他费用": other_costs,
            "总成本": round(total_cost, 2),
            "说明": notes,
            "维修地点": location,
            "工程师姓名": engineer_name,
        })

    async def complete_dispatch(
        self,
        dispatch_id: int,
        session: AsyncSession = Depends(get_async_session),
        _=Depends(allow_supervisor),
    ):
        result = await session.execute(
            select(EngineerDispatch).where(EngineerDispatch.id == dispatch_id)
        )
        dispatch = result.scalar_one_or_none()
        if not dispatch:
            return BaseResponse(code=404, msg="调派记录不存在")
        dispatch.调派状态 = "completed"
        await session.commit()
        return BaseResponse(data={"id": dispatch.id, "状态": "completed"})
