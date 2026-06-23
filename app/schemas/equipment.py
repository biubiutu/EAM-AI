from typing import Optional
from pydantic import BaseModel, Field


class EquipmentCreate(BaseModel):
    设备编码: str
    设备名称: str
    设备型号: Optional[str] = ""
    设备分类: Optional[str] = ""
    所属厂区: Optional[str] = ""
    所属车间: Optional[str] = ""
    所属产线: Optional[str] = ""
    设备状态: str = Field(default="in_use")
    入库放置地点: Optional[str] = ""
    报废地点: Optional[str] = ""
    状态备注: Optional[str] = ""
    采购日期: Optional[str] = ""
    质保到期日: Optional[str] = ""
    制造商: Optional[str] = ""
    供应商ID: Optional[int] = None


class EquipmentUpdate(BaseModel):
    设备名称: Optional[str] = None
    设备型号: Optional[str] = None
    设备分类: Optional[str] = None
    所属厂区: Optional[str] = None
    所属车间: Optional[str] = None
    所属产线: Optional[str] = None
    设备状态: Optional[str] = None
    入库放置地点: Optional[str] = None
    报废地点: Optional[str] = None
    状态备注: Optional[str] = None
    采购日期: Optional[str] = None
    质保到期日: Optional[str] = None
    制造商: Optional[str] = None
    供应商ID: Optional[int] = None


class EquipmentStatusChange(BaseModel):
    设备状态: str
    状态备注: Optional[str] = ""