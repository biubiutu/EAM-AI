from fastapi import APIRouter
from .engineer.router import router as engineer_router
from .supervisor.router import router as supervisor_router
from .purchaser.router import router as purchaser_router
from .leader.router import router as leader_router
from .common.router import router as common_router
from .admin.router import admin_router as admin_router_obj

router = APIRouter(prefix="/api/v1")

router.include_router(engineer_router)
router.include_router(supervisor_router)
router.include_router(purchaser_router)
router.include_router(leader_router)
router.include_router(common_router)
router.include_router(admin_router_obj.router, prefix="/admin")