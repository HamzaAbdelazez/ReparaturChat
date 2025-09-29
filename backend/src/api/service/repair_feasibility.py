import logging
import re
from typing import Dict, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.database.table_models import User, Device, UploadedPdf, DocumentChunk, Tool, DocumentTool
from api.models.repair_analysis import RepairFeasibilityResult

logger = logging.getLogger(__name__)


class RepairFeasibilityService:
    """Enhanced service for repair feasibility analysis."""
    
    # Skill requirements for different repair types
    REPAIR_TYPE_REQUIREMENTS = {
        "disassembly": {"min_skill": 2, "min_experience": 1, "tools": ["screwdriver"]},
        "soldering": {"min_skill": 4, "min_experience": 3, "tools": ["soldering iron"], "space": 3},
        "component_replacement": {"min_skill": 3, "min_experience": 2, "tools": ["screwdriver", "pliers"]},
        "electrical_work": {"min_skill": 4, "min_experience": 3, "tools": ["multimeter", "wire stripper"]},
        "calibration": {"min_skill": 5, "min_experience": 4, "tools": ["multimeter"]},
        "software_repair": {"min_skill": 2, "min_experience": 1, "tools": []},
        "mechanical_repair": {"min_skill": 3, "min_experience": 2, "tools": ["wrench", "pliers"]},
        "cleaning": {"min_skill": 1, "min_experience": 1, "tools": []},
        "lubrication": {"min_skill": 2, "min_experience": 1, "tools": []},
        "adjustment": {"min_skill": 2, "min_experience": 1, "tools": ["screwdriver"]}
    }
    
    # Physical requirements for device categories
    DEVICE_PHYSICAL_REQUIREMENTS = {
        "washing machine": {"min_strength": 4, "min_space": 4, "weight_kg": 70},
        "refrigerator": {"min_strength": 5, "min_space": 5, "weight_kg": 100},
        "dishwasher": {"min_strength": 4, "min_space": 4, "weight_kg": 50},
        "oven": {"min_strength": 3, "min_space": 3, "weight_kg": 30},
        "air conditioner": {"min_strength": 4, "min_space": 4, "weight_kg": 40},
        "smartphone": {"min_strength": 1, "min_space": 1, "weight_kg": 0.2},
        "laptop": {"min_strength": 1, "min_space": 2, "weight_kg": 2},
        "tv": {"min_strength": 2, "min_space": 3, "weight_kg": 15},
        "vacuum cleaner": {"min_strength": 2, "min_space": 2, "weight_kg": 5},
        "microwave": {"min_strength": 2, "min_space": 3, "weight_kg": 15}
    }
    
    # Safety considerations for different repairs
    SAFETY_REQUIREMENTS = {
        "electrical": {
            "risk_level": "high",
            "requirements": ["Turn off power", "Use insulated tools", "Check voltage"],
            "min_experience": 3
        },
        "gas": {
            "risk_level": "very_high", 
            "requirements": ["Turn off gas supply", "Ventilation", "Gas leak detector"],
            "min_experience": 4
        },
        "refrigerant": {
            "risk_level": "high",
            "requirements": ["Proper ventilation", "Refrigerant recovery", "Pressure gauge"],
            "min_experience": 4
        },
        "high_temperature": {
            "risk_level": "medium",
            "requirements": ["Heat-resistant gloves", "Ventilation", "Fire extinguisher"],
            "min_experience": 2
        }
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze_repair_feasibility(
        self,
        user_id: UUID,
        device_id: UUID,
        document_id: UUID
    ) -> RepairFeasibilityResult:
        """Comprehensive repair feasibility analysis."""
        try:
            # Get user, device, and document data
            user = await self._get_user(user_id)
            device = await self._get_device(device_id)
            document_content = await self._get_document_content(document_id)
            required_tools = await self._get_required_tools(document_id)
            
            # Analyze repair requirements from document
            repair_analysis = await self._analyze_repair_requirements(document_content)
            
            # Check various feasibility factors
            skill_check = self._check_skill_requirements(user, device, repair_analysis)
            physical_check = self._check_physical_requirements(user, device)
            tool_check = self._check_tool_availability(required_tools, user)
            safety_check = self._check_safety_requirements(user, repair_analysis)
            complexity_check = self._check_complexity_alignment(user, device, repair_analysis)
            
            # Compile warnings and recommendations
            warnings = []
            recommendations = []
            
            self._add_skill_warnings(skill_check, warnings, recommendations)
            self._add_physical_warnings(physical_check, warnings, recommendations)
            self._add_tool_warnings(tool_check, warnings, recommendations)
            self._add_safety_warnings(safety_check, warnings, recommendations)
            self._add_complexity_warnings(complexity_check, warnings, recommendations)
            
            # Determine overall feasibility
            is_feasible = self._determine_overall_feasibility(
                skill_check, physical_check, tool_check, safety_check, complexity_check
            )
            
            return RepairFeasibilityResult(
                is_feasible=is_feasible,
                user_skill_score=self._calculate_user_skill_score(user),
                required_skill_score=repair_analysis.get("complexity_score", 3),
                complexity_score=device.repair_complexity,
                warnings=warnings,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing repair feasibility: {e}")
            raise
    
    async def _get_user(self, user_id: UUID) -> User:
        """Get user with profile data."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        return user
    
    async def _get_device(self, device_id: UUID) -> Device:
        """Get device data."""
        result = await self.db.execute(select(Device).where(Device.id == device_id))
        device = result.scalar_one_or_none()
        if not device:
            raise ValueError("Device not found")
        return device
    
    async def _get_document_content(self, document_id: UUID) -> str:
        """Get document text content."""
        result = await self.db.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        chunks = result.scalars().all()
        return " ".join([chunk.content for chunk in chunks])
    
    async def _get_required_tools(self, document_id: UUID) -> List[Tool]:
        """Get tools required for this repair."""
        result = await self.db.execute(
            select(DocumentTool).options(selectinload(DocumentTool.tool))
            .where(DocumentTool.document_id == document_id)
        )
        document_tools = result.scalars().all()
        return [dt.tool for dt in document_tools if dt.tool]
    
    async def _analyze_repair_requirements(self, content: str) -> Dict:
        """Analyze repair requirements from document content."""
        content_lower = content.lower()
        
        # Detect repair types
        repair_types = []
        for repair_type in self.REPAIR_TYPE_REQUIREMENTS:
            if repair_type.replace("_", " ") in content_lower:
                repair_types.append(repair_type)
        
        # Detect safety requirements
        safety_types = []
        if any(word in content_lower for word in ["electrical", "voltage", "power", "current"]):
            safety_types.append("electrical")
        if any(word in content_lower for word in ["gas", "propane", "natural gas"]):
            safety_types.append("gas")
        if any(word in content_lower for word in ["refrigerant", "coolant", "freon"]):
            safety_types.append("refrigerant")
        if any(word in content_lower for word in ["hot", "heat", "temperature", "burning"]):
            safety_types.append("high_temperature")
        
        # Estimate complexity from keywords
        complexity_indicators = [
            "carefully", "precision", "exact", "calibrate", "professional", 
            "experience required", "advanced", "specialized", "critical"
        ]
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in content_lower)
        complexity_score = min(5, max(1, complexity_score + 1))
        
        # Count steps (rough estimate)
        step_count = len(re.findall(r'\b\d+[\.\)]\s', content)) or len(re.findall(r'step \d+', content_lower))
        
        return {
            "repair_types": repair_types,
            "safety_types": safety_types,
            "complexity_score": complexity_score,
            "estimated_steps": step_count,
            "estimated_time_hours": max(1, step_count * 0.25)  # 15 minutes per step
        }
    
    def _check_skill_requirements(self, user: User, device: Device, repair_analysis: Dict) -> Dict:
        """Check if user meets skill requirements."""
        required_skill = max(
            device.repair_complexity,
            repair_analysis.get("complexity_score", 3)
        )
        
        # Check specific repair type requirements
        max_repair_skill = 1
        for repair_type in repair_analysis.get("repair_types", []):
            if repair_type in self.REPAIR_TYPE_REQUIREMENTS:
                req = self.REPAIR_TYPE_REQUIREMENTS[repair_type]
                max_repair_skill = max(max_repair_skill, req["min_skill"])
        
        required_skill = max(required_skill, max_repair_skill)
        
        return {
            "meets_requirements": user.skill_level >= required_skill,
            "user_skill": user.skill_level,
            "required_skill": required_skill,
            "skill_gap": max(0, required_skill - user.skill_level)
        }
    
    def _check_physical_requirements(self, user: User, device: Device) -> Dict:
        """Check physical capability requirements."""
        device_req = self.DEVICE_PHYSICAL_REQUIREMENTS.get(
            device.category.lower(), 
            {"min_strength": 2, "min_space": 2, "weight_kg": 5}
        )
        
        return {
            "meets_strength": user.physical_strength >= device_req["min_strength"],
            "meets_space": user.available_space >= device_req["min_space"],
            "required_strength": device_req["min_strength"],
            "required_space": device_req["min_space"],
            "device_weight": device_req["weight_kg"]
        }
    
    def _check_tool_availability(self, required_tools: List[Tool], user: User) -> Dict:
        """Check tool requirements."""
        # Simplified check - in real implementation, check user's tool inventory
        return {
            "has_all_tools": len(required_tools) <= user.experience_level,  # Simplified assumption
            "required_tools": [tool.name for tool in required_tools],
            "missing_tools": [tool.name for tool in required_tools[user.experience_level:]],
            "tool_count": len(required_tools)
        }
    
    def _check_safety_requirements(self, user: User, repair_analysis: Dict) -> Dict:
        """Check safety requirement compliance."""
        safety_issues = []
        max_risk_level = "low"
        
        for safety_type in repair_analysis.get("safety_types", []):
            if safety_type in self.SAFETY_REQUIREMENTS:
                safety_req = self.SAFETY_REQUIREMENTS[safety_type]
                if user.experience_level < safety_req["min_experience"]:
                    safety_issues.append({
                        "type": safety_type,
                        "risk_level": safety_req["risk_level"],
                        "requirements": safety_req["requirements"]
                    })
                max_risk_level = safety_req["risk_level"]
        
        return {
            "is_safe": len(safety_issues) == 0,
            "safety_issues": safety_issues,
            "max_risk_level": max_risk_level
        }
    
    def _check_complexity_alignment(self, user: User, device: Device, repair_analysis: Dict) -> Dict:
        """Check overall complexity alignment."""
        estimated_time = repair_analysis.get("estimated_time_hours", 2)
        user_time_multiplier = {1: 3.0, 2: 2.0, 3: 1.5, 4: 1.0, 5: 0.8}
        
        actual_time = estimated_time * user_time_multiplier.get(user.skill_level, 2.0)
        
        return {
            "estimated_time": estimated_time,
            "user_adjusted_time": actual_time,
            "complexity_match": device.repair_complexity <= user.skill_level + 1,
            "time_manageable": actual_time <= 8.0  # Max 8 hours for feasibility
        }
    
    def _calculate_user_skill_score(self, user: User) -> int:
        """Calculate overall user skill score."""
        return int((user.skill_level + user.experience_level + user.physical_strength) / 3)
    
    def _determine_overall_feasibility(self, *checks) -> bool:
        """Determine if repair is overall feasible."""
        skill_check, physical_check, tool_check, safety_check, complexity_check = checks
        
        # Critical requirements
        if not safety_check["is_safe"]:
            return False
        
        if not skill_check["meets_requirements"]:
            return False
        
        # Important requirements (2 out of 3 must pass)
        important_checks = [
            physical_check["meets_strength"] and physical_check["meets_space"],
            tool_check["has_all_tools"],
            complexity_check["complexity_match"] and complexity_check["time_manageable"]
        ]
        
        return sum(important_checks) >= 2
    
    def _add_skill_warnings(self, skill_check: Dict, warnings: List, recommendations: List):
        """Add skill-related warnings and recommendations."""
        if not skill_check["meets_requirements"]:
            warnings.append(f"Your skill level ({skill_check['user_skill']}) is below required ({skill_check['required_skill']})")
            recommendations.append("Consider taking a repair course or watching tutorial videos")
            recommendations.append("Start with simpler repairs to build experience")
    
    def _add_physical_warnings(self, physical_check: Dict, warnings: List, recommendations: List):
        """Add physical requirement warnings."""
        if not physical_check["meets_strength"]:
            warnings.append(f"This repair requires higher physical strength ({physical_check['required_strength']}/5)")
            recommendations.append("Consider getting help with heavy lifting")
        
        if not physical_check["meets_space"]:
            warnings.append(f"This repair requires more workspace ({physical_check['required_space']}/5)")
            recommendations.append("Ensure adequate workspace before starting")
    
    def _add_tool_warnings(self, tool_check: Dict, warnings: List, recommendations: List):
        """Add tool-related warnings."""
        if not tool_check["has_all_tools"]:
            warnings.append(f"You may be missing required tools: {', '.join(tool_check['missing_tools'])}")
            recommendations.append("Acquire all necessary tools before starting")
            recommendations.append("Consider renting specialized tools")
    
    def _add_safety_warnings(self, safety_check: Dict, warnings: List, recommendations: List):
        """Add safety warnings."""
        if not safety_check["is_safe"]:
            for issue in safety_check["safety_issues"]:
                warnings.append(f"High risk {issue['type']} work detected - {issue['risk_level']} risk level")
                recommendations.extend([f"Ensure: {req}" for req in issue["requirements"]])
    
    def _add_complexity_warnings(self, complexity_check: Dict, warnings: List, recommendations: List):
        """Add complexity warnings."""
        if not complexity_check["time_manageable"]:
            warnings.append(f"Estimated repair time is {complexity_check['user_adjusted_time']:.1f} hours")
            recommendations.append("Plan for multiple sessions if needed")
        
        if not complexity_check["complexity_match"]:
            warnings.append("This repair may be more complex than your current skill level")
            recommendations.append("Consider professional assistance for complex steps")