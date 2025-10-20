import logging
from fastapi import APIRouter, Depends
from api.routers.dependencies import db_dependency
from api.database.table_models import Device, Tool, User
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/setup", tags=["setup"])

@router.post("/populate-sample-data")
async def populate_sample_data(db=Depends(db_dependency)):
    """Populate sample devices and tools for testing."""
    try:
        # Sample devices
        devices = [
            Device(
                manufacturer="Samsung", model="Galaxy S20", category="smartphone", 
                warranty_period_months=24, repair_complexity=2
            ),
            Device(
                manufacturer="Apple", model="iPhone 12", category="smartphone",
                warranty_period_months=12, repair_complexity=3
            ),
            Device(
                manufacturer="Bosch", model="WAW28460", category="washing machine",
                warranty_period_months=24, repair_complexity=4
            ),
            Device(
                manufacturer="Sony", model="WH-1000XM4", category="headphones",
                warranty_period_months=12, repair_complexity=2
            )
        ]
        
        # Sample tools
        tools = [
            Tool(
                name="Phillips Screwdriver Set", description="Set of Phillips head screwdrivers",
                min_price=15.99, max_price=25.99, reusability_score=5, category="hand_tools"
            ),
            Tool(
                name="Torx Screwdriver Set", description="Set of Torx screwdrivers for electronics", 
                min_price=12.99, max_price=22.99, reusability_score=4, category="hand_tools"
            ),
            Tool(
                name="Plastic Spudger Set", description="Plastic tools for phone/tablet repair",
                min_price=8.99, max_price=15.99, reusability_score=3, category="hand_tools"
            )
        ]
        
        # Add to database
        db.add_all(devices + tools)
        await db.commit()
        
        return {
            "message": "Sample data populated successfully",
            "devices_added": len(devices),
            "tools_added": len(tools)
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error populating sample data: {e}")
        return {"error": str(e)}

@router.get("/list-devices")
async def list_devices(db=Depends(db_dependency)):
    """List all devices in database."""
    try:
        from sqlalchemy import select
        result = await db.execute(select(Device))
        devices = result.scalars().all()
        return {
            "devices": [
                {
                    "id": str(device.id),
                    "manufacturer": device.manufacturer,
                    "model": device.model,
                    "category": device.category,
                    "repair_complexity": device.repair_complexity
                }
                for device in devices
            ]
        }
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        return {"error": str(e)}