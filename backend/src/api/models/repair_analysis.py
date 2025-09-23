import uuid
from typing import List, Optional
from pydantic import BaseModel


class RepairFeasibilityResult(BaseModel):
    """Result of repair feasibility analysis for US32."""
    is_feasible: bool
    user_skill_score: int
    required_skill_score: int
    complexity_score: int
    warnings: List[str]
    recommendations: List[str]


class CostEstimation(BaseModel):
    """Cost estimation for repairs - US5, US19, US29."""
    tools_cost: float
    parts_cost: float
    time_cost: float  # estimated time * hourly rate
    total_cost: float
    tool_details: List[dict]  # Tool names, prices, reusability
    

class TimeEstimation(BaseModel):
    """Time estimation for repairs - US5, US30."""
    base_time_hours: float
    user_adjustment_factor: float  # based on skill level
    tool_acquisition_time_hours: float
    total_time_hours: float


class RepairComparison(BaseModel):
    """Comparison between self-repair and professional service - US29, US30."""
    self_repair: dict  # cost, time, feasibility
    professional_service: dict  # cost, time, provider info
    recommendation: str  # "self_repair" or "professional"
    cost_difference: float
    time_difference: float


class ToolReusabilityAnalysis(BaseModel):
    """Tool reusability analysis for US19.2."""
    tool_id: uuid.UUID
    tool_name: str
    reusability_score: int  # 1-5
    estimated_future_uses: int
    cost_per_use: float
    recommendation: str  # "buy", "rent", "borrow"