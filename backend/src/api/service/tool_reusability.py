import logging
from typing import Dict, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from api.database.table_models import Tool, User, UserDevice, Device
from api.models.repair_analysis import ToolReusabilityAnalysis

logger = logging.getLogger(__name__)


class ToolReusabilityService:
    """Enhanced service for tool reusability analysis ."""
    
    # Tool category mapping to device categories
    TOOL_DEVICE_COMPATIBILITY = {
        "screwdriver": ["smartphone", "laptop", "tv", "washing machine", "dishwasher", "oven"],
        "wrench": ["washing machine", "dishwasher", "air conditioner", "refrigerator"],
        "pliers": ["smartphone", "laptop", "tv", "washing machine", "dishwasher"],
        "multimeter": ["smartphone", "laptop", "tv", "air conditioner", "washing machine"],
        "hammer": ["washing machine", "dishwasher", "refrigerator", "oven"],
        "allen key": ["furniture", "laptop", "tv", "washing machine"],
        "torx screwdriver": ["smartphone", "laptop", "tv"],
        "spudger": ["smartphone", "laptop", "tv"],
        "heat gun": ["smartphone", "laptop", "tv", "air conditioner"],
        "soldering iron": ["smartphone", "laptop", "tv"],
        "socket wrench": ["washing machine", "dishwasher", "air conditioner", "refrigerator"],
        "wire stripper": ["washing machine", "dishwasher", "air conditioner", "tv"],
        "pump wrench": ["washing machine", "dishwasher"],
        "refrigerant gauge": ["air conditioner", "refrigerator"],
        "diagnostic scanner": ["washing machine", "dishwasher", "air conditioner"]
    }
    
    # Repair complexity requirements for tools
    TOOL_COMPLEXITY_REQUIREMENTS = {
        "basic": ["screwdriver", "pliers", "hammer", "allen key"],
        "intermediate": ["wrench", "multimeter", "socket wrench", "wire stripper"],
        "advanced": ["heat gun", "soldering iron", "diagnostic scanner", "refrigerant gauge"],
        "specialist": ["torx screwdriver", "spudger", "pump wrench"]
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze_tool_reusability(
        self, 
        tool_id: UUID, 
        user_id: UUID
    ) -> ToolReusabilityAnalysis:
        """Comprehensive tool reusability analysis."""
        try:
            # Get tool and user data
            tool_result = await self.db.execute(select(Tool).where(Tool.id == tool_id))
            tool = tool_result.scalar_one_or_none()
            
            user_result = await self.db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            
            if not tool or not user:
                raise ValueError("Tool or user not found")
            
            # Get user's devices
            user_devices = await self._get_user_devices(user_id)
            
            # Analyze reusability factors
            compatibility_score = await self._calculate_compatibility_score(tool, user_devices)
            future_usage_estimate = await self._estimate_future_usage(tool, user, user_devices)
            skill_alignment = await self._check_skill_alignment(tool, user)
            cost_effectiveness = await self._calculate_cost_effectiveness(tool, future_usage_estimate)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                compatibility_score, future_usage_estimate, skill_alignment, cost_effectiveness
            )
            
            return ToolReusabilityAnalysis(
                tool_id=tool_id,
                tool_name=tool.name,
                reusability_score=self._calculate_overall_score(
                    compatibility_score, future_usage_estimate, skill_alignment
                ),
                estimated_future_uses=future_usage_estimate,
                cost_per_use=cost_effectiveness,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Error analyzing tool reusability: {e}")
            raise
    
    async def _get_user_devices(self, user_id: UUID) -> List[Device]:
        """Get all devices owned by the user."""
        query = select(UserDevice).where(UserDevice.user_id == user_id)
        result = await self.db.execute(query)
        user_devices = result.scalars().all()
        
        devices = []
        for ud in user_devices:
            device_result = await self.db.execute(select(Device).where(Device.id == ud.device_id))
            device = device_result.scalar_one_or_none()
            if device:
                devices.append(device)
        
        return devices
    
    async def _calculate_compatibility_score(self, tool: Tool, devices: List[Device]) -> int:
        """Calculate how compatible the tool is with user's devices."""
        if not devices:
            return 1
        
        tool_name_lower = tool.name.lower()
        compatible_count = 0
        
        for device in devices:
            device_category = device.category.lower()
            
            # Check direct compatibility
            for tool_type, compatible_categories in self.TOOL_DEVICE_COMPATIBILITY.items():
                if tool_type in tool_name_lower:
                    if any(cat in device_category for cat in compatible_categories):
                        compatible_count += 1
                    break
        
        # Score from 1-5 based on compatibility percentage
        compatibility_ratio = compatible_count / len(devices) if devices else 0
        return max(1, min(5, int(compatibility_ratio * 5) + 1))
    
    async def _estimate_future_usage(self, tool: Tool, user: User, devices: List[Device]) -> int:
        """Estimate future usage based on user profile and devices."""
        base_usage = tool.reusability_score or 1
        
        # Adjust based on user experience level
        experience_multiplier = {1: 0.5, 2: 0.7, 3: 1.0, 4: 1.5, 5: 2.0}
        usage_multiplier = experience_multiplier.get(user.experience_level, 1.0)
        
        # Adjust based on number of compatible devices
        device_multiplier = min(len(devices) * 0.5, 3.0)
        
        # Adjust based on tool type
        tool_name_lower = tool.name.lower()
        if any(basic_tool in tool_name_lower for basic_tool in self.TOOL_COMPLEXITY_REQUIREMENTS["basic"]):
            type_multiplier = 2.0  # Basic tools used more frequently
        elif any(adv_tool in tool_name_lower for adv_tool in self.TOOL_COMPLEXITY_REQUIREMENTS["advanced"]):
            type_multiplier = 0.5  # Advanced tools used less frequently
        else:
            type_multiplier = 1.0
        
        estimated_usage = int(base_usage * usage_multiplier * device_multiplier * type_multiplier)
        return max(1, min(50, estimated_usage))  # Cap between 1-50 uses
    
    async def _check_skill_alignment(self, tool: Tool, user: User) -> bool:
        """Check if user's skill level aligns with tool complexity."""
        tool_name_lower = tool.name.lower()
        
        # Determine required skill level for tool
        required_skill = 1
        if any(basic_tool in tool_name_lower for basic_tool in self.TOOL_COMPLEXITY_REQUIREMENTS["basic"]):
            required_skill = 1
        elif any(int_tool in tool_name_lower for int_tool in self.TOOL_COMPLEXITY_REQUIREMENTS["intermediate"]):
            required_skill = 3
        elif any(adv_tool in tool_name_lower for adv_tool in self.TOOL_COMPLEXITY_REQUIREMENTS["advanced"]):
            required_skill = 4
        elif any(spec_tool in tool_name_lower for spec_tool in self.TOOL_COMPLEXITY_REQUIREMENTS["specialist"]):
            required_skill = 5
        
        return user.skill_level >= required_skill
    
    async def _calculate_cost_effectiveness(self, tool: Tool, estimated_uses: int) -> float:
        """Calculate cost per use."""
        tool_price = tool.min_price or 25.0  # Default price if not available
        return round(tool_price / max(estimated_uses, 1), 2)
    
    def _calculate_overall_score(self, compatibility: int, future_uses: int, skill_aligned: bool) -> int:
        """Calculate overall reusability score (1-5)."""
        # Normalize future uses to 1-5 scale
        usage_score = min(5, max(1, future_uses // 5))
        
        # Weight the factors
        score = (compatibility * 0.4) + (usage_score * 0.4) + (3 if skill_aligned else 1) * 0.2
        
        return int(round(score))
    
    def _generate_recommendation(
        self, 
        compatibility: int, 
        future_uses: int, 
        skill_aligned: bool, 
        cost_per_use: float
    ) -> str:
        """Generate purchase recommendation."""
        
        if not skill_aligned:
            return "consider_training"  # Consider getting training first
        
        if cost_per_use <= 2.0 and compatibility >= 3:
            return "buy"  # Definitely worth buying
        elif cost_per_use <= 5.0 and future_uses >= 5:
            return "buy"  # Good value for money
        elif cost_per_use <= 15.0 and compatibility >= 2:
            return "rent"  # Consider renting for occasional use
        elif compatibility >= 4 and future_uses >= 10:
            return "buy"  # High compatibility makes it worthwhile
        else:
            return "borrow"  # Not cost-effective to buy
    
    async def get_reusability_breakdown(self, tool_id: UUID, user_id: UUID) -> Dict:
        """Get detailed breakdown of reusability factors."""
        try:
            tool_result = await self.db.execute(select(Tool).where(Tool.id == tool_id))
            tool = tool_result.scalar_one_or_none()
            
            user_result = await self.db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            
            if not tool or not user:
                raise ValueError("Tool or user not found")
            
            user_devices = await self._get_user_devices(user_id)
            
            return {
                "tool_name": tool.name,
                "user_devices_count": len(user_devices),
                "compatible_devices": [
                    device.manufacturer + " " + device.model 
                    for device in user_devices
                ],
                "compatibility_score": await self._calculate_compatibility_score(tool, user_devices),
                "estimated_future_uses": await self._estimate_future_usage(tool, user, user_devices),
                "skill_aligned": await self._check_skill_alignment(tool, user),
                "cost_per_use": await self._calculate_cost_effectiveness(
                    tool, await self._estimate_future_usage(tool, user, user_devices)
                ),
                "user_skill_level": user.skill_level,
                "user_experience_level": user.experience_level
            }
            
        except Exception as e:
            logger.error(f"Error getting reusability breakdown: {e}")
            raise ValueError(f"Failed to get reusability breakdown: {str(e)}")