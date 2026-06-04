from typing import Optional, Generic, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    code: int = 200
    msg: str = "success"
    data: Optional[T] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": {}
            }
        }


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PaginatedData(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int