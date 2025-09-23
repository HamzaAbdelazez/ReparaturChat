import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DeviceIn(BaseModel):
    manufacturer: str
    model: str
    category: str
    warranty_period_months: Optional[int] = 24
    repair_complexity: Optional[int] = 3


class DeviceOut(BaseModel):
    id: uuid.UUID
    manufacturer: str
    model: str
    category: str
    warranty_period_months: int
    repair_complexity: int


class UserDeviceIn(BaseModel):
    device_id: uuid.UUID
    purchase_date: Optional[datetime] = None
    warranty_status: Optional[str] = "unknown"


class UserDeviceOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    device_id: uuid.UUID
    purchase_date: Optional[datetime]
    warranty_status: str
    device: Optional[DeviceOut] = None


class WarrantyCheckResult(BaseModel):
    is_under_warranty: bool
    warranty_expires_at: Optional[datetime]
    warranty_status: str
    days_remaining: Optional[int]