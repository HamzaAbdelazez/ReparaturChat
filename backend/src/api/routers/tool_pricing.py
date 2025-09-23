import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from api.routers.dependencies import db_dependency
from api.service.tool_pricing import ToolPricingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tool-pricing", tags=["tool-pricing"])


@router.post("/update-prices/{tool_id}")
async def update_tool_prices(
    tool_id: UUID,
    background_tasks: BackgroundTasks,
    db = Depends(db_dependency)
):
    """Update tool prices from external sources (US19)."""
    try:
        service = ToolPricingService(db)
        
        # Run price update in background
        background_tasks.add_task(service.update_tool_prices, tool_id)
        
        return {"message": "Price update started", "tool_id": str(tool_id)}
        
    except Exception as e:
        logger.error(f"Error starting price update: {e}")
        raise HTTPException(status_code=500, detail="Failed to start price update")


@router.get("/prices/{tool_id}")
async def get_tool_prices(
    tool_id: UUID,
    db = Depends(db_dependency)
):
    """Get current tool prices from database (US19)."""
    try:
        service = ToolPricingService(db)
        prices = await service.get_tool_prices(tool_id)
        
        return {
            "tool_id": str(tool_id),
            "prices": prices
        }
        
    except Exception as e:
        logger.error(f"Error getting tool prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tool prices")


@router.get("/cheapest/{tool_id}")
async def get_cheapest_price(
    tool_id: UUID,
    db = Depends(db_dependency)
):
    """Get the cheapest price for a tool (US19)."""
    try:
        service = ToolPricingService(db)
        cheapest = await service.get_cheapest_price(tool_id)
        
        if not cheapest:
            raise HTTPException(status_code=404, detail="No prices found for this tool")
        
        return {
            "tool_id": str(tool_id),
            "cheapest_price": cheapest
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cheapest price: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cheapest price")


@router.post("/compare-prices")
async def compare_tool_prices(
    tool_ids: List[UUID],
    db = Depends(db_dependency)
):
    """Compare prices across multiple tools (US19)."""
    try:
        service = ToolPricingService(db)
        comparison = await service.compare_tool_prices(tool_ids)
        
        return {
            "comparison": comparison,
            "total_tools": len(tool_ids)
        }
        
    except Exception as e:
        logger.error(f"Error comparing tool prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare tool prices")