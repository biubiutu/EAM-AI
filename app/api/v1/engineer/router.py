from fastapi import APIRouter
from .knowledge import KnowledgeRouter
from .work_order import WorkOrderRouter
from .diagnosis import DiagnosisRouter
from .predictive import PredictiveRouter
from .exam import ExamRouter
from .feedback import FeedbackRouter

router = APIRouter(prefix="/engineer", tags=["设备工程师端"])

router.include_router(KnowledgeRouter()._register_routes(), prefix="/knowledge")
router.include_router(WorkOrderRouter()._register_routes(), prefix="/work-order")
router.include_router(DiagnosisRouter()._register_routes(), prefix="/diagnosis")
router.include_router(PredictiveRouter()._register_routes(), prefix="/predictive")
router.include_router(ExamRouter()._register_routes(), prefix="/exam")
router.include_router(FeedbackRouter()._register_routes(), prefix="/feedback")
