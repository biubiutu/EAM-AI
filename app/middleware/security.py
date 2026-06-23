"""
安全中间件 - 限流、安全头、请求审计
"""
import time
import re
import logging
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# 简单内存限流（生产环境建议用 Redis）
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 60  # 每分钟请求上限
_RATE_WINDOW = 60  # 窗口秒数


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 仅对 API 路由限流
        if request.url.path.startswith("/api/"):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            window = _rate_limit_store[client_ip]
            # 清理过期记录
            _rate_limit_store[client_ip] = [t for t in window if now - t < _RATE_WINDOW]
            if len(_rate_limit_store[client_ip]) >= _RATE_LIMIT:
                logger.warning("IP %s 触发限流", client_ip)
                return JSONResponse(
                    status_code=429,
                    content={"code": 429, "msg": "请求过于频繁，请稍后重试"},
                )
            _rate_limit_store[client_ip].append(now)

        response = await call_next(request)

        # 安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


# 密码强度检查
PASSWORD_MIN_LENGTH = 8

def check_password_strength(password: str) -> tuple[bool, str]:
    """检查密码强度，返回 (是否合格, 消息)"""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"密码长度至少 {PASSWORD_MIN_LENGTH} 位"
    if not re.search(r"[A-Za-z]", password):
        return False, "密码需包含字母"
    if not re.search(r"\d", password):
        return False, "密码需包含数字"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_+=\-\[\]\\\\]", password):
        return False, "密码需包含特殊字符"
    return True, "密码强度合格"