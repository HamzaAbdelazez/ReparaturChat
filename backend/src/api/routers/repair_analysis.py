import logging
from uuid import UUID
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.routers.dependencies import db_dependency
from api.service.repair_analysis import RepairAnalysisService
from api.service.repair_feasibility import RepairFeasibilityService
from api.service.tool_reusability import ToolReusabilityService
from api.service.chat_based_analysis import ChatBasedAnalysisService
from api.models.repair_analysis import (
    RepairFeasibilityResult, CostEstimation, TimeEstimation, 
    RepairComparison, ToolReusabilityAnalysis
)


class ChatBasedAnalysisRequest(BaseModel):
    user_id: UUID
    problem_description: str
    chat_history: List[Dict[str, Any]] = []
    document_id: Optional[UUID] = None
    llm_model: str = "gemma3"

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repair-analysis", tags=["repair-analysis"])


@router.get("/feasibility")
async def check_repair_feasibility(
    user_id: UUID,
    device_id: UUID,
    document_id: UUID,
    db = Depends(db_dependency)
) -> RepairFeasibilityResult:
    """Enhanced repair feasibility check."""
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
    """Estimate total repair costs including tools and time."""
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
    """Estimate repair time based on user skill level."""
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
    """Compare self-repair vs professional service."""
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
    """Enhanced tool reusability analysis."""
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
    """Get detailed breakdown of tool reusability factors."""
    try:
        service = ToolReusabilityService(db)
        return await service.get_reusability_breakdown(tool_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting reusability breakdown: {e}")
        raise HTTPException(status_code=500, detail="Failed to get reusability breakdown")


@router.post("/chat-based-analysis")
async def analyze_chat_based_problem(
    request: ChatBasedAnalysisRequest,
    db = Depends(db_dependency)
) -> Dict[str, Any]:
    """Analyze repair problem from chat description."""
    try:
        service = ChatBasedAnalysisService(db)
        return await service.analyze_chat_problem(
            user_id=request.user_id,
            problem_description=request.problem_description,
            chat_history=request.chat_history,
            document_id=request.document_id,
            llm_model=request.llm_model
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in chat-based analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze chat-based problem")