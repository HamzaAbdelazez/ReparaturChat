"""
Chat-based repair analysis service.
Analyzes repair problems described in natural language chat conversations.
"""

import logging
from typing import Dict, List, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.database.table_models import User, Device, UserDevice
from api.service.repair_feasibility import RepairFeasibilityService
from api.service.device_extractor import DeviceExtractorService
from api.models.repair_analysis import RepairFeasibilityResult

logger = logging.getLogger(__name__)


class ChatBasedAnalysisService:
    """Service for analyzing repair problems from chat descriptions."""
    
    # Common repair problems and their characteristics
    COMMON_PROBLEMS = {
        'not_turning_on': {
            'keywords': ['not turning on', 'won\'t start', 'dead', 'no power', 'not working'],
            'complexity_score': 3,
            'required_skills': ['basic_electrical', 'troubleshooting'],
            'estimated_time_hours': 2.0,
            'estimated_cost_range': '20-100'
        },
        'screen_broken': {
            'keywords': ['screen broken', 'cracked screen', 'display not working', 'black screen'],
            'complexity_score': 4,
            'required_skills': ['precision_work', 'component_replacement'],
            'estimated_time_hours': 3.0,
            'estimated_cost_range': '50-200'
        },
        'overheating': {
            'keywords': ['overheating', 'hot', 'getting warm', 'burning smell'],
            'complexity_score': 3,
            'required_skills': ['thermal_management', 'cleaning'],
            'estimated_time_hours': 1.5,
            'estimated_cost_range': '10-50'
        },
        'strange_noise': {
            'keywords': ['strange noise', 'loud noise', 'grinding', 'squeaking', 'rattling'],
            'complexity_score': 2,
            'required_skills': ['mechanical_inspection', 'lubrication'],
            'estimated_time_hours': 1.0,
            'estimated_cost_range': '5-30'
        },
        'connection_issues': {
            'keywords': ['not connecting', 'wifi problems', 'bluetooth issues', 'network problems'],
            'complexity_score': 2,
            'required_skills': ['software_troubleshooting', 'network_basics'],
            'estimated_time_hours': 0.5,
            'estimated_cost_range': '0-20'
        },
        'battery_issues': {
            'keywords': ['battery', 'not charging', 'short battery life', 'power draining'],
            'complexity_score': 3,
            'required_skills': ['battery_replacement', 'electrical_safety'],
            'estimated_time_hours': 1.5,
            'estimated_cost_range': '20-80'
        }
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.feasibility_service = RepairFeasibilityService(db)
        self.device_extractor = DeviceExtractorService(db)
    
    async def analyze_chat_problem(
        self, 
        user_id: UUID, 
        problem_description: str,
        chat_history: List[Dict[str, Any]] = None,
        document_id: UUID = None
    ) -> Dict[str, Any]:
        """
        Analyze a repair problem described in chat with automatic device detection.
        
        Args:
            user_id: User performing the repair
            problem_description: Main problem description from chat
            chat_history: Recent chat messages for context
            document_id: Optional PDF document ID for device extraction
            
        Returns:
            Comprehensive analysis including feasibility, costs, and recommendations
        """
        try:
            # Get user information
            user = await self._get_user(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Extract device information from text
            device_info = await self._extract_device_info(problem_description, chat_history, document_id)
            if not device_info:
                # Provide generic analysis without specific device
                device_info = {
                    'device_id': None,
                    'manufacturer': 'Unknown',
                    'model': 'Generic Device',
                    'category': 'Electronics',
                    'source': 'generic'
                }
            
            # Get or create device object
            device = await self._get_or_create_device(device_info)
            
            # Analyze the problem description
            problem_analysis = self._analyze_problem_description(problem_description)
            
            # Check repair feasibility
            feasibility = await self._check_chat_based_feasibility(
                user, device, problem_analysis
            )
            
            # Estimate costs and time
            cost_estimate = self._estimate_costs_from_problem(problem_analysis, device)
            time_estimate = self._estimate_time_from_problem(problem_analysis, user)
            
            # Generate suggestions
            suggestions = self._generate_solutions(problem_analysis, device)
            
            # Create comprehensive analysis result
            analysis_result = {
                'analysis_source': 'chat_based',
                'problem_summary': problem_description,
                'detected_problem_type': problem_analysis.get('problem_type', 'unknown'),
                'device_info': {
                    'manufacturer': device_info.get('manufacturer', 'Unknown'),
                    'model': device_info.get('model', 'Generic Device'),
                    'category': device_info.get('category', 'Electronics'),
                    'source': device_info.get('source', 'generic'),
                    'confidence': device_info.get('confidence', 0),
                    'extracted_text': device_info.get('extracted_text', '')
                },
                'feasibility': {
                    'is_feasible': feasibility['is_feasible'],
                    'user_skill_score': user.skill_level,
                    'required_skill_score': problem_analysis.get('complexity_score', 3),
                    'warnings': feasibility.get('warnings', []),
                    'recommendations': feasibility.get('recommendations', [])
                },
                'cost_estimate': cost_estimate,
                'time_estimate': time_estimate,
                'suggested_solutions': suggestions,
                'comparison': {
                    'self_repair': {
                        'cost': self._parse_cost_range(cost_estimate)[0],
                        'time': time_estimate.split('-')[0] if '-' in time_estimate else time_estimate.split()[0],
                        'feasible': feasibility['is_feasible']
                    },
                    'professional_service': {
                        'cost': self._parse_cost_range(cost_estimate)[1] * 2,  # Professional typically costs more
                        'time': 2.0,  # Assume 2 hours for professional service
                    },
                    'recommendation': 'self_repair' if feasibility['is_feasible'] and user.skill_level >= 3 else 'professional_service'
                }
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in chat-based analysis: {e}")
            raise
    
    async def _get_user(self, user_id: UUID) -> User:
        """Get user from database."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def _extract_device_info(self, problem_description: str, chat_history: List[Dict[str, Any]] = None, document_id: UUID = None) -> Optional[Dict]:
        """Extract device information from various sources."""
        try:
            # First try to extract from PDF document if provided
            if document_id:
                device_info = await self.device_extractor.extract_device_from_pdf_content(document_id)
                if device_info and device_info.get('confidence', 0) > 50:
                    return device_info
            
            # Try to extract from problem description
            device_info = await self.device_extractor.extract_device_from_text(problem_description)
            if device_info and device_info.get('confidence', 0) > 30:
                return device_info
            
            # Try to extract from chat history
            if chat_history:
                chat_result = self.device_extractor.extract_device_from_chat_history(chat_history)
                if chat_result and 'text_to_process' in chat_result:
                    device_info = await self.device_extractor.extract_device_from_text(chat_result['text_to_process'])
                    if device_info and device_info.get('confidence', 0) > 20:
                        return device_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting device info: {e}")
            return None
    
    async def _get_or_create_device(self, device_info: Dict) -> Device:
        """Get existing device or create a mock device object for analysis."""
        try:
            # If we have a device_id from database match, use it
            if device_info.get('device_id'):
                result = await self.db.execute(select(Device).where(Device.id == device_info['device_id']))
                device = result.scalar_one_or_none()
                if device:
                    return device
            
            # Create a mock device object for analysis purposes
            # This won't be saved to database, just used for repair analysis
            mock_device = Device(
                manufacturer=device_info.get('manufacturer', 'Unknown'),
                model=device_info.get('model', 'Generic Device'),
                category=device_info.get('category', 'Electronics'),
            )
            
            return mock_device
            
        except Exception as e:
            logger.error(f"Error getting/creating device: {e}")
            # Return a generic device for analysis
            return Device(
                manufacturer='Unknown',
                model='Generic Device',
                category='Electronics',
            )
    
    def _analyze_problem_description(self, description: str) -> Dict[str, Any]:
        """
        Analyze the problem description to identify problem type and characteristics.
        """
        description_lower = description.lower()
        
        # Try to match against common problems
        for problem_type, problem_data in self.COMMON_PROBLEMS.items():
            if any(keyword in description_lower for keyword in problem_data['keywords']):
                return {
                    'problem_type': problem_type,
                    'complexity_score': problem_data['complexity_score'],
                    'required_skills': problem_data['required_skills'],
                    'estimated_time_hours': problem_data['estimated_time_hours'],
                    'estimated_cost_range': problem_data['estimated_cost_range']
                }
        
        # Default analysis for unrecognized problems
        return {
            'problem_type': 'general_issue',
            'complexity_score': 3,
            'required_skills': ['general_repair'],
            'estimated_time_hours': 2.0,
            'estimated_cost_range': '20-80'
        }
    
    async def _check_chat_based_feasibility(
        self, 
        user: User, 
        device: Device, 
        problem_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if the user can feasibly perform this repair."""
        
        warnings = []
        recommendations = []
        
        # Check skill level vs complexity
        required_skill = problem_analysis.get('complexity_score', 3)
        user_skill = user.skill_level
        
        is_feasible = user_skill >= required_skill
        
        # Add warnings based on problem type
        problem_type = problem_analysis.get('problem_type', '')
        
        if 'electrical' in str(problem_analysis.get('required_skills', [])):
            warnings.append("This repair involves electrical components. Ensure power is disconnected.")
        
        if problem_type == 'screen_broken':
            warnings.append("Screen replacement requires precision and proper tools.")
            recommendations.append("Consider using a professional service for expensive devices.")
        
        if problem_type == 'overheating':
            recommendations.append("Check for dust buildup and ensure proper ventilation.")
        
        if not is_feasible:
            recommendations.append(f"Your skill level ({user_skill}/5) is below recommended ({required_skill}/5). Consider professional service.")
        
        return {
            'is_feasible': is_feasible,
            'warnings': warnings,
            'recommendations': recommendations
        }
    
    def _estimate_costs_from_problem(self, problem_analysis: Dict[str, Any], device: Device) -> str:
        """Estimate repair costs based on problem type and device."""
        base_cost_range = problem_analysis.get('estimated_cost_range', '20-80')
        
        # Adjust based on device category
        if device.category and 'smartphone' in device.category.lower():
            # Smartphones often have higher part costs
            return self._adjust_cost_range(base_cost_range, 1.5)
        elif device.category and 'laptop' in device.category.lower():
            # Laptops can vary widely
            return self._adjust_cost_range(base_cost_range, 2.0)
        
        return base_cost_range
    
    def _estimate_time_from_problem(self, problem_analysis: Dict[str, Any], user: User) -> str:
        """Estimate repair time based on problem and user skill."""
        base_time = problem_analysis.get('estimated_time_hours', 2.0)
        
        # Adjust based on user skill level
        skill_multiplier = {1: 2.0, 2: 1.5, 3: 1.0, 4: 0.8, 5: 0.6}
        adjusted_time = base_time * skill_multiplier.get(user.skill_level, 1.0)
        
        return f"{adjusted_time:.1f} hours"
    
    def _generate_solutions(self, problem_analysis: Dict[str, Any], device: Device) -> List[str]:
        """Generate suggested solutions based on problem type."""
        problem_type = problem_analysis.get('problem_type', '')
        
        solutions = {
            'not_turning_on': [
                "Check power cable and connections",
                "Test with different power outlet",
                "Inspect internal fuses",
                "Check power button functionality"
            ],
            'screen_broken': [
                "Order replacement screen for your specific model",
                "Gather precision screwdrivers and plastic tools",
                "Follow step-by-step disassembly guide",
                "Test display connection before full assembly"
            ],
            'overheating': [
                "Clean dust from vents and fans",
                "Check thermal paste on CPU/GPU",
                "Verify fan operation",
                "Ensure adequate ventilation space"
            ],
            'strange_noise': [
                "Identify source of noise (fan, hard drive, etc.)",
                "Clean and lubricate moving parts",
                "Check for loose components",
                "Replace worn mechanical parts if needed"
            ],
            'connection_issues': [
                "Reset network settings",
                "Update drivers and firmware",
                "Check antenna connections",
                "Test with different networks"
            ],
            'battery_issues': [
                "Check charging cable and adapter",
                "Calibrate battery (full charge/discharge cycle)",
                "Replace battery if degraded",
                "Update power management software"
            ]
        }
        
        return solutions.get(problem_type, [
            "Identify the root cause of the problem",
            "Gather appropriate tools and replacement parts",
            "Follow manufacturer's service manual if available",
            "Test thoroughly after repair"
        ])
    
    def _adjust_cost_range(self, cost_range: str, multiplier: float) -> str:
        """Adjust a cost range by a multiplier."""
        try:
            # Parse "20-80" format
            if '-' in cost_range:
                low, high = cost_range.split('-')
                low_val = int(low) * multiplier
                high_val = int(high) * multiplier
                return f"{int(low_val)}-{int(high_val)}"
            else:
                # Single value
                val = int(cost_range) * multiplier
                return str(int(val))
        except:
            return cost_range
    
    def _parse_cost_range(self, cost_range: str) -> tuple:
        """Parse cost range string to get low and high values."""
        try:
            if '-' in cost_range:
                low, high = cost_range.split('-')
                return (float(low), float(high))
            else:
                val = float(cost_range)
                return (val, val)
        except:
            return (20.0, 80.0)  # Default range