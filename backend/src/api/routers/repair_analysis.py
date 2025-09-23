import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from api.routers.dependencies import db_dependency
from api.service.repair_analysis import RepairAnalysisService
from api.service.repair_feasibility import RepairFeasibilityService
from api.service.tool_reusability import ToolReusabilityService
from api.models.repair_analysis import (
    RepairFeasibilityResult, CostEstimation, TimeEstimation, 
    RepairComparison, ToolReusabilityAnalysis
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repair-analysis", tags=["repair-analysis"])


@router.get("/feasibility")
async def check_repair_feasibility(
    user_id: UUID,
    device_id: UUID,
    document_id: UUID,
    db = Depends(db_dependency)
) -> RepairFeasibilityResult:
    """Enhanced repair feasibility check (US32)."""
    try:
        service = RepairFeasibilityService(db)
        return await service.analyze_repair_feasibility(user_id, device_id, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in feasibility check: {e}")
        raise HTTPException(status_code=500, detail="Failed to check repair feasibility")


@router.get("/cost-estimation")
async def estimate_repair_costs(
    user_id: UUID,
    document_id: UUID,
    db = Depends(db_dependency)
) -> CostEstimation:
    """Estimate total repair costs including tools and time (US5, US19)."""
    try:
        return await RepairAnalysisService.estimate_repair_costs(
            user_id, document_id, db
        )
    except Exception as e:
        logger.error(f"Error in cost estimation: {e}")
        raise HTTPException(status_code=500, detail="Failed to estimate repair costs")


@router.get("/time-estimation")
async def estimate_repair_time(
    user_id: UUID,
    document_id: UUID,
    db = Depends(db_dependency)
) -> TimeEstimation:
    """Estimate repair time based on user skill level (US5, US30)."""
    try:
        return await RepairAnalysisService.estimate_repair_time(
            user_id, document_id, db
        )
    except Exception as e:
        logger.error(f"Error in time estimation: {e}")
        raise HTTPException(status_code=500, detail="Failed to estimate repair time")


@router.get("/compare-options")
async def compare_repair_options(
    user_id: UUID,
    device_id: UUID,
    document_id: UUID,
    db = Depends(db_dependency)
) -> RepairComparison:
    """Compare self-repair vs professional service (US29, US30)."""
    try:
        return await RepairAnalysisService.compare_repair_options(
            user_id, device_id, document_id, db
        )
    except Exception as e:
        logger.error(f"Error in repair comparison: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare repair options")


@router.get("/tool-reusability/{tool_id}")
async def analyze_tool_reusability(
    tool_id: UUID,
    user_id: UUID,
    db = Depends(db_dependency)
) -> ToolReusabilityAnalysis:
    """Enhanced tool reusability analysis (US19.2)."""
    try:
        service = ToolReusabilityService(db)
        return await service.analyze_tool_reusability(tool_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in tool reusability analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze tool reusability")


@router.get("/tool-reusability-breakdown/{tool_id}")
async def get_tool_reusability_breakdown(
    tool_id: UUID,
    user_id: UUID,
    db = Depends(db_dependency)
):
    """Get detailed breakdown of tool reusability factors (US19.2)."""
    try:
        service = ToolReusabilityService(db)
        return await service.get_reusability_breakdown(tool_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting reusability breakdown: {e}")
        raise HTTPException(status_code=500, detail="Failed to get reusability breakdown")