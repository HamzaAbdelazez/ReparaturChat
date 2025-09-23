import logging
from typing import List, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.database.table_models import User, Device, Tool, DocumentTool, UploadedPdf
from api.models.repair_analysis import (
    RepairFeasibilityResult, CostEstimation, TimeEstimation, 
    RepairComparison, ToolReusabilityAnalysis
)

logger = logging.getLogger(__name__)


class RepairAnalysisService:
    """Service for repair analysis functionality (US32, US5, US29, US30, US19.2)."""
    
    @staticmethod
    async def check_repair_feasibility(
        user_id: UUID,
        device_id: UUID,
        document_id: UUID,
        db: AsyncSession
    ) -> RepairFeasibilityResult:
        """Check if user can feasibly perform the repair (US32)."""
        try:
            # Get user profile
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if not user:
                raise ValueError("User not found")
            
            # Get device complexity
            device_result = await db.execute(select(Device).where(Device.id == device_id))
            device = device_result.scalar_one_or_none()
            if not device:
                raise ValueError("Device not found")
            
            # Calculate user capability score (average of skill, strength, experience)
            user_skill_score = (user.skill_level + user.physical_strength + user.experience_level) // 3
            required_skill_score = device.repair_complexity
            
            warnings = []
            recommendations = []
            
            # Check feasibility
            is_feasible = user_skill_score >= required_skill_score
            
            if not is_feasible:
                warnings.append(f"Repair complexity ({required_skill_score}) exceeds your skill level ({user_skill_score})")
                recommendations.append("Consider professional repair service")
                recommendations.append("Improve skills with simpler repairs first")
            
            # Additional checks
            if user.physical_strength < 3 and device.repair_complexity >= 4:
                warnings.append("This repair may require significant physical strength")
            
            if user.available_space < 3 and device.category in ["washing machine", "refrigerator", "large appliance"]:
                warnings.append("This repair may require significant workspace")
            
            if user.experience_level < 2:
                recommendations.append("Watch tutorial videos before starting")
                recommendations.append("Have backup contact for professional help")
            
            return RepairFeasibilityResult(
                is_feasible=is_feasible,
                user_skill_score=user_skill_score,
                required_skill_score=required_skill_score,
                complexity_score=device.repair_complexity,
                warnings=warnings,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error checking repair feasibility: {e}")
            raise
    
    @staticmethod
    async def estimate_repair_costs(
        user_id: UUID,
        document_id: UUID,
        db: AsyncSession
    ) -> CostEstimation:
        """Estimate total repair costs including tools and time (US5, US19)."""
        try:
            # Get user for skill level adjustment
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            
            # Get tools required for this document
            query = select(DocumentTool).options(selectinload(DocumentTool.tool)).where(
                DocumentTool.document_id == document_id
            )
            result = await db.execute(query)
            document_tools = result.scalars().all()
            
            tools_cost = 0.0
            tool_details = []
            
            for dt in document_tools:
                if dt.tool:
                    tool_cost = dt.tool.min_price or 0.0
                    tools_cost += tool_cost
                    tool_details.append({
                        "name": dt.tool.name,
                        "price": tool_cost,
                        "reusability_score": dt.tool.reusability_score or 1
                    })
            
            # Estimate parts cost (simplified - could be enhanced with actual parts data)
            parts_cost = tools_cost * 0.3  # Assume parts cost 30% of tools cost
            
            # Estimate time cost based on user skill level
            base_time_hours = 4.0  # Default repair time
            skill_multiplier = {1: 2.0, 2: 1.5, 3: 1.0, 4: 0.8, 5: 0.6}
            time_multiplier = skill_multiplier.get(user.skill_level if user else 3, 1.0)
            
            estimated_time = base_time_hours * time_multiplier
            hourly_rate = 25.0  # €25/hour as opportunity cost
            time_cost = estimated_time * hourly_rate
            
            total_cost = tools_cost + parts_cost + time_cost
            
            return CostEstimation(
                tools_cost=tools_cost,
                parts_cost=parts_cost,
                time_cost=time_cost,
                total_cost=total_cost,
                tool_details=tool_details
            )
            
        except Exception as e:
            logger.error(f"Error estimating repair costs: {e}")
            raise
    
    @staticmethod
    async def estimate_repair_time(
        user_id: UUID,
        document_id: UUID,
        db: AsyncSession
    ) -> TimeEstimation:
        """Estimate repair time based on user skill level (US5, US30)."""
        try:
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            
            base_time_hours = 4.0  # Base repair time
            
            # Adjust based on user skill level
            skill_adjustments = {1: 2.0, 2: 1.5, 3: 1.0, 4: 0.8, 5: 0.6}
            adjustment_factor = skill_adjustments.get(user.skill_level if user else 3, 1.0)
            
            # Add tool acquisition time
            tool_acquisition_time = 2.0  # Hours to acquire tools
            
            total_time = (base_time_hours * adjustment_factor) + tool_acquisition_time
            
            return TimeEstimation(
                base_time_hours=base_time_hours,
                user_adjustment_factor=adjustment_factor,
                tool_acquisition_time_hours=tool_acquisition_time,
                total_time_hours=total_time
            )
            
        except Exception as e:
            logger.error(f"Error estimating repair time: {e}")
            raise
    
    @staticmethod
    async def compare_repair_options(
        user_id: UUID,
        device_id: UUID,
        document_id: UUID,
        db: AsyncSession
    ) -> RepairComparison:
        """Compare self-repair vs professional service (US29, US30)."""
        try:
            # Get self-repair estimates
            cost_est = await RepairAnalysisService.estimate_repair_costs(user_id, document_id, db)
            time_est = await RepairAnalysisService.estimate_repair_time(user_id, document_id, db)
            feasibility = await RepairAnalysisService.check_repair_feasibility(user_id, device_id, document_id, db)
            
            # Professional service estimates (simplified)
            professional_cost = 150.0  # Average professional repair cost
            professional_time = 2.0    # Hours including travel/wait time
            
            self_repair = {
                "cost": cost_est.total_cost,
                "time": time_est.total_time_hours,
                "feasible": feasibility.is_feasible
            }
            
            professional_service = {
                "cost": professional_cost,
                "time": professional_time,
                "guaranteed": True
            }
            
            cost_difference = cost_est.total_cost - professional_cost
            time_difference = time_est.total_time_hours - professional_time
            
            # Make recommendation
            if not feasibility.is_feasible:
                recommendation = "professional"
            elif cost_difference > 100 and time_difference > 4:
                recommendation = "professional"
            else:
                recommendation = "self_repair"
            
            return RepairComparison(
                self_repair=self_repair,
                professional_service=professional_service,
                recommendation=recommendation,
                cost_difference=cost_difference,
                time_difference=time_difference
            )
            
        except Exception as e:
            logger.error(f"Error comparing repair options: {e}")
            raise
    
    @staticmethod
    async def analyze_tool_reusability(
        tool_id: UUID,
        user_id: UUID,
        db: AsyncSession
    ) -> ToolReusabilityAnalysis:
        """Analyze tool reusability for a specific user (US19.2)."""
        try:
            tool_result = await db.execute(select(Tool).where(Tool.id == tool_id))
            tool = tool_result.scalar_one_or_none()
            if not tool:
                raise ValueError("Tool not found")
            
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            
            # Estimate future uses based on user's device collection and experience level
            estimated_future_uses = tool.reusability_score or 1
            if user and user.experience_level >= 3:
                estimated_future_uses *= 2  # Experienced users likely to do more repairs
            
            cost_per_use = (tool.min_price or 0.0) / max(estimated_future_uses, 1)
            
            # Make recommendation
            if cost_per_use <= 10.0:
                recommendation = "buy"
            elif cost_per_use <= 25.0:
                recommendation = "rent"
            else:
                recommendation = "borrow"
            
            return ToolReusabilityAnalysis(
                tool_id=tool_id,
                tool_name=tool.name,
                reusability_score=tool.reusability_score or 1,
                estimated_future_uses=estimated_future_uses,
                cost_per_use=cost_per_use,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Error analyzing tool reusability: {e}")
            raise