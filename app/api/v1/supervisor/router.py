from fastapi import APIRouter
from .requisition import RequisitionRouter
from .equipment import EquipmentRouter
from .sharing import SharingRouter
from .dispatch import DispatchRouter

router = APIRouter(prefix="/supervisor", tags=["主管端"])

router.include_router(RequisitionRouter()._register_routes(), prefix="/requisition")
router.include_router(EquipmentRouter()._register_routes(), prefix="/equipment")
router.include_router(SharingRouter()._register_routes(), prefix="/sharing")
router.include_router(DispatchRouter()._register_routes(), prefix="/dispatch")
