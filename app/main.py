from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router as v1_router
from app.core.exceptions import AppException
from app.middleware.middleware import RequestLoggingMiddleware, app_exception_handler, general_exception_handler
from app.config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI驱动的智能设备全生命周期管理系统",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(v1_router)


@app.get("/health", tags=["系统"])
async def health_check():
    return {"code": 200, "msg": "success", "data": {"status": "healthy"}}