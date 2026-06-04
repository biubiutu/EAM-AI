from fastapi import APIRouter
from .auth import AuthRouter
from .upload import UploadRouter

router = APIRouter(prefix="/common", tags=["公共服务"])
router.include_router(AuthRouter()._register_routes(), prefix="/auth")
router.include_router(UploadRouter()._register_routes(), prefix="/upload")
