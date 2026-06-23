from fastapi import Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentStatusChange
from app.core.security import allow_supervisor, get_current_user
from app.core.database import get_async_session
from app.models.equipment import Equipment
from app.config.constants import EquipmentStatus


class EquipmentRouter(BaseRouter):

    def _register_routes(self):
        self.router.get("/list", response_model=BaseResponse, summary="设备列表",
                        tags=["主管-设备台账"])(self.list_equipment)
        self.router.get("/{equipment_id}", response_model=BaseResponse, summary="设备详情",
                        tags=["主管-设备台账"])(self.get_equipment)
        self.router.post("/", response_model=BaseResponse, summary="创建设备",
                         tags=["主管-设备台账"])(self.create_equipment)
        self.router.put("/{equipment_id}", response_model=BaseResponse, summary="更新设备",
                        tags=["主管-设备台账"])(self.update_equipment)
        self.router.post("/{equipment_id}/status", response_model=BaseResponse, summary="设备状态流转",
                         tags=["主管-设备台账"])(self.change_status)
        return self.router

    async def list_equipment(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        设备状态: str = Query("", alias="设备状态"),
        所属厂区: str = Query("", alias="所属厂区"),
        db: AsyncSession = Depends(get_async_session),
        _=Depends(allow_supervisor),
    ):
        query = select(Equipment).order_by(Equipment.id.desc())
        count_query = select(func.count()).select_from(Equipment)

        if 设备状态:
            query = query.where(Equipment.设备状态 == 设备状态)
            count_query = count_query.where(Equipment.设备状态 == 设备状态)
        if 所属厂区:
            query = query.where(Equipment.所属厂区 == 所属厂区)
            count_query = count_query.where(Equipment.所属厂区 == 所属厂区)

        total = (await db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        result = await db.execute(query.offset(offset).limit(page_size))
        items = result.scalars().all()

        data = []
        for eq in items:
            d = {c.name: getattr(eq, c.name) for c in eq.__table__.columns}
            d["id"] = eq.id
            data.append(d)

        return BaseResponse(data={
            "items": data,
            "total": total,
            "page": page,
            "page_size": page_size,
        })

    async def get_equipment(
        self, equipment_id: int,
        db: AsyncSession = Depends(get_async_session),
        _=Depends(allow_supervisor),
    ):
        result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
        eq = result.scalar_one_or_none()
        if not eq:
            return BaseResponse(code=404, msg="设备不存在")
        d = {c.name: getattr(eq, c.name) for c in eq.__table__.columns}
        d["id"] = eq.id
        return BaseResponse(data=d)

    async def create_equipment(
        self, request: EquipmentCreate,
        db: AsyncSession = Depends(get_async_session),
        _=Depends(allow_supervisor),
    ):
        eq = Equipment(**request.model_dump())
        db.add(eq)
        await db.commit()
        await db.refresh(eq)
        return BaseResponse(data={"id": eq.id}, msg="创建成功")

    async def update_equipment(
        self, equipment_id: int, request: EquipmentUpdate,
        db: AsyncSession = Depends(get_async_session),
        _=Depends(allow_supervisor),
    ):
        result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
        eq = result.scalar_one_or_none()
        if not eq:
            return BaseResponse(code=404, msg="设备不存在")

        update_data = request.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(eq, k, v)
        await db.commit()
        await db.refresh(eq)
        return BaseResponse(msg="更新成功")

    async def change_status(
        self, equipment_id: int, request: EquipmentStatusChange,
        db: AsyncSession = Depends(get_async_session),
        _=Depends(allow_supervisor),
    ):
        result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
        eq = result.scalar_one_or_none()
        if not eq:
            return BaseResponse(code=404, msg="设备不存在")

        new_status = request.设备状态
        valid = {
            EquipmentStatus.IN_USE,
            EquipmentStatus.IN_STORAGE,
            EquipmentStatus.PENDING_REPAIR,
            EquipmentStatus.UNDER_REPAIR,
            EquipmentStatus.SCRAPPED,
        }
        if new_status not in valid:
            return BaseResponse(code=400, msg=f"无效状态: {new_status}")

        eq.设备状态 = new_status
        eq.状态变更时间 = datetime.now()
        if request.状态备注:
            eq.状态备注 = request.状态备注
        await db.commit()
        return BaseResponse(msg=f"状态已变更为 {new_status}")


equipment_router = EquipmentRouter()