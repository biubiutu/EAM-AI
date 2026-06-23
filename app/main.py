from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from contextlib import asynccontextmanager
from app.api.v1.router import router as v1_router
from app.core.exceptions import AppException
from app.middleware.middleware import RequestLoggingMiddleware, app_exception_handler, general_exception_handler
from app.middleware.security import RateLimitMiddleware
from app.config.settings import settings
from app.core.database import engine
from app.models.base import Base
import logging
import os

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:
        logger.warning("Database init skipped: %s", exc)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI驱动的智能设备全生命周期管理系统",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(v1_router)

# 挂载前端静态文件
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir, html=True), name="frontend")

    @app.get("/", tags=["前端"], include_in_schema=False)
    async def redirect_to_frontend():
        return RedirectResponse(url="/static/main.html")


@app.get("/health", tags=["系统"])
async def health_check():
    return {"code": 200, "msg": "success", "data": {"status": "healthy"}}