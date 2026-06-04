import functools
import logging
from abc import abstractmethod
from typing import Callable

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse

from app.schemas.common import BaseResponse

logger = logging.getLogger(__name__)


class BaseRouter:
    """路由基类，提供统一的路由配置"""

    def __init__(self):
        logger.info(f"Initializing {self.__class__.__name__}")
        self.router = APIRouter()

    @abstractmethod
    def _register_routes(self) -> APIRouter:
        """
        注册路由，子类需实现此方法来定义具体路由
        """
        pass

    def get_router(self) -> APIRouter:
        """获取APIRouter实例"""
        return self.router

    def base_endpoint(self, func: Callable):
        """
        统一装饰器：包装端点，统一处理错误和响应格式
        """

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                if isinstance(result, (StreamingResponse, FileResponse, Response)):
                    return result
                if isinstance(result, BaseResponse):
                    return result
                return BaseResponse(data=result)
            except ValueError as e:
                logger.error(f"Error in {func.__name__}() - {str(e)}", exc_info=True)
                return BaseResponse(code=400, msg=str(e))
            except HTTPException as e:
                logger.error(f"HTTPException in {func.__name__}() - {str(e)}", exc_info=True)
                return BaseResponse(code=e.status_code, msg=str(e.detail))
            except Exception as e:
                logger.error(f"Error in {func.__name__}() - {str(e)}", exc_info=True)
                return BaseResponse(code=500, msg=f"服务器内部错误: {str(e)}")

        wrapper._is_base_endpoint = True
        return wrapper
