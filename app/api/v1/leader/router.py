from fastapi import APIRouter
from .approval import ApprovalRouter
from .lcc import LCCRouter
from .dashboard import DashboardRouter

router = APIRouter(prefix="/leader", tags=["领导端"])

router.include_router(ApprovalRouter()._register_routes(), prefix="/approval")
router.include_router(LCCRouter()._register_routes(), prefix="/lcc")
router.include_router(DashboardRouter()._register_routes(), prefix="/dashboard")
