import logging
from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from api.routers.dependencies import db_dependency
from api.database.table_models import Device, UserDevice, User
from api.models.device import (
    DeviceIn, DeviceOut, UserDeviceIn, UserDeviceOut, WarrantyCheckResult
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/", response_model=DeviceOut)
async def create_device(
    device_data: DeviceIn,
    db: AsyncSession = Depends(db_dependency)
):
    """Create a new device model."""
    try:
        device = Device(
            manufacturer=device_data.manufacturer,
            model=device_data.model,
            category=device_data.category,
            warranty_period_months=device_data.warranty_period_months,
            repair_complexity=device_data.repair_complexity
        )
        
        db.add(device)
        await db.commit()
        await db.refresh(device)
        
        return DeviceOut(
            id=device.id,
            manufacturer=device.manufacturer,
            model=device.model,
            category=device.category,
            warranty_period_months=device.warranty_period_months,
            repair_complexity=device.repair_complexity
        )
    except Exception as e:
        logger.error(f"Error creating device: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create device")


@router.get("/search")
async def search_devices(
    manufacturer: str = Query(None),
    model: str = Query(None),
    category: str = Query(None),
    db: AsyncSession = Depends(db_dependency)
):
    """Search for devices by manufacturer, model, or category."""
    try:
        query = select(Device)
        
        if manufacturer:
            query = query.where(Device.manufacturer.ilike(f"%{manufacturer}%"))
        if model:
            query = query.where(Device.model.ilike(f"%{model}%"))
        if category:
            query = query.where(Device.category.ilike(f"%{category}%"))
        
        result = await db.execute(query)
        devices = result.scalars().all()
        
        return [
            DeviceOut(
                id=device.id,
                manufacturer=device.manufacturer,
                model=device.model,
                category=device.category,
                warranty_period_months=device.warranty_period_months,
                repair_complexity=device.repair_complexity
            )
            for device in devices
        ]
    except Exception as e:
        logger.error(f"Error searching devices: {e}")
        raise HTTPException(status_code=500, detail="Failed to search devices")


@router.post("/user-devices/", response_model=UserDeviceOut)
async def add_user_device(
    user_id: UUID,
    device_data: UserDeviceIn,
    db: AsyncSession = Depends(db_dependency)
):
    """Add a device to user's collection ."""
    try:
        # Check if user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if device exists
        device_result = await db.execute(select(Device).where(Device.id == device_data.device_id))
        device = device_result.scalar_one_or_none()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        user_device = UserDevice(
            user_id=user_id,
            device_id=device_data.device_id,
            purchase_date=device_data.purchase_date,
            warranty_status=device_data.warranty_status
        )
        
        db.add(user_device)
        await db.commit()
        await db.refresh(user_device)
        
        return UserDeviceOut(
            id=user_device.id,
            user_id=user_device.user_id,
            device_id=user_device.device_id,
            purchase_date=user_device.purchase_date,
            warranty_status=user_device.warranty_status,
            device=DeviceOut(
                id=device.id,
                manufacturer=device.manufacturer,
                model=device.model,
                category=device.category,
                warranty_period_months=device.warranty_period_months,
                repair_complexity=device.repair_complexity
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding user device: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add user device")


@router.get("/user-devices/{user_id}")
async def get_user_devices(
    user_id: UUID,
    db: AsyncSession = Depends(db_dependency)
):
    """Get all devices owned by a user."""
    try:
        query = select(UserDevice).options(selectinload(UserDevice.device)).where(UserDevice.user_id == user_id)
        result = await db.execute(query)
        user_devices = result.scalars().all()
        
        return [
            UserDeviceOut(
                id=ud.id,
                user_id=ud.user_id,
                device_id=ud.device_id,
                purchase_date=ud.purchase_date,
                warranty_status=ud.warranty_status,
                device=DeviceOut(
                    id=ud.device.id,
                    manufacturer=ud.device.manufacturer,
                    model=ud.device.model,
                    category=ud.device.category,
                    warranty_period_months=ud.device.warranty_period_months,
                    repair_complexity=ud.device.repair_complexity
                ) if ud.device else None
            )
            for ud in user_devices
        ]
    except Exception as e:
        logger.error(f"Error getting user devices: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user devices")


@router.get("/warranty-check/{user_device_id}")
async def check_warranty(
    user_device_id: UUID,
    db: AsyncSession = Depends(db_dependency)
):
    """Check warranty status for a user device."""
    try:
        query = select(UserDevice).options(selectinload(UserDevice.device)).where(UserDevice.id == user_device_id)
        result = await db.execute(query)
        user_device = result.scalar_one_or_none()
        
        if not user_device:
            raise HTTPException(status_code=404, detail="User device not found")
        
        if not user_device.purchase_date or not user_device.device:
            return WarrantyCheckResult(
                is_under_warranty=False,
                warranty_expires_at=None,
                warranty_status="unknown",
                days_remaining=None
            )
        
        warranty_expires_at = user_device.purchase_date + timedelta(days=user_device.device.warranty_period_months * 30)
        current_date = datetime.now(user_device.purchase_date.tzinfo)
        days_remaining = (warranty_expires_at - current_date).days
        
        is_under_warranty = days_remaining > 0
        warranty_status = "active" if is_under_warranty else "expired"
        
        # Update warranty status in database
        user_device.warranty_status = warranty_status
        await db.commit()
        
        return WarrantyCheckResult(
            is_under_warranty=is_under_warranty,
            warranty_expires_at=warranty_expires_at,
            warranty_status=warranty_status,
            days_remaining=days_remaining if is_under_warranty else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking warranty: {e}")
        raise HTTPException(status_code=500, detail="Failed to check warranty")