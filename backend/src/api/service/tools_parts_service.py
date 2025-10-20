"""
Tools and Parts Extraction Service
Extracts tools and parts from LLM responses and manages user preferences
"""

import re
import json
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

class ToolsPartsExtractor:
    """Extract tools and parts from LLM responses using pattern matching."""
    
    def __init__(self):
        # Common tool patterns
        self.tool_patterns = [
            r'\b(?:screwdriver|phillips|flathead|torx|hex|allen)\b',
            r'\b(?:pliers|needle-nose|wire strippers)\b',
            r'\b(?:multimeter|voltmeter|ammeter)\b',
            r'\b(?:soldering iron|solder|flux)\b',
            r'\b(?:heat gun|hair dryer)\b',
            r'\b(?:spudger|prying tool|plastic tool)\b',
            r'\b(?:tweezers|forceps)\b',
            r'\b(?:wrench|socket|ratchet)\b',
            r'\b(?:drill|bits)\b',
            r'\b(?:safety glasses|gloves|anti-static)\b'
        ]
        
        # Common parts patterns
        self.part_patterns = [
            r'\b(?:battery|batteries)\b',
            r'\b(?:screen|display|lcd|oled)\b',
            r'\b(?:cable|wire|connector)\b',
            r'\b(?:fuse|capacitor|resistor)\b',
            r'\b(?:fan|cooling)\b',
            r'\b(?:ram|memory|storage)\b',
            r'\b(?:motherboard|circuit board)\b',
            r'\b(?:speaker|microphone)\b',
            r'\b(?:camera|sensor)\b',
            r'\b(?:gasket|seal|o-ring)\b'
        ]
    
    def extract_tools_and_parts(self, response_text: str) -> Dict[str, Any]:
        """Extract tools and parts from LLM response text."""
        
        # Convert to lowercase for matching
        text_lower = response_text.lower()
        
        # Extract tools
        tools = []
        for pattern in self.tool_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            tools.extend(matches)
        
        # Extract parts
        parts = []
        for pattern in self.part_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            parts.extend(matches)
        
        # Remove duplicates and capitalize
        tools = list(set([tool.title() for tool in tools]))
        parts = list(set([part.title() for part in parts]))
        
        # Try to extract cost estimates
        cost_estimates = self._extract_cost_estimates(response_text)
        
        return {
            "tools": tools,
            "parts": parts,
            "cost_estimates": cost_estimates,
            "has_tools_parts": len(tools) > 0 or len(parts) > 0
        }
    
    def _extract_cost_estimates(self, text: str) -> List[Dict[str, Any]]:
        """Extract cost estimates from text."""
        
        cost_patterns = [
            r'\$(\d+(?:\.\d{2})?)',  # $15.99
            r'€(\d+(?:\.\d{2})?)',   # €15.99
            r'(\d+(?:\.\d{2})?) ?(?:dollars?|euros?|USD|EUR)',  # 15 dollars
        ]
        
        estimates = []
        for pattern in cost_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = float(match) if isinstance(match, str) else float(match[0])
                    estimates.append({
                        "amount": amount,
                        "currency": "USD" if "$" in text or "dollar" in text.lower() else "EUR"
                    })
                except ValueError:
                    continue
        
        return estimates

class UserPreferenceService:
    """Manage user preferences for showing tools and parts."""
    
    @staticmethod
    def get_user_preference(user_id: str, db: Session) -> bool:
        """Get user preference for showing tools/parts. Returns True by default."""
        try:
            # For now, return True (show tools/parts) by default
            # In a full implementation, this would query the database
            return True
        except Exception:
            return True
    
    @staticmethod
    def set_user_preference(user_id: str, show_tools_parts: bool, db: Session) -> bool:
        """Set user preference for showing tools/parts."""
        try:
            # For now, just return True
            # In a full implementation, this would update the database
            return True
        except Exception:
            return False

class ToolsPartsResponse:
    """Enhanced response with tools and parts information."""
    
    def __init__(self, original_response: Dict[str, Any], tools_parts_data: Dict[str, Any]):
        self.original_response = original_response
        self.tools_parts_data = tools_parts_data
    
    def to_dict(self, include_tools_parts: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format."""
        
        response = self.original_response.copy()
        
        if include_tools_parts and self.tools_parts_data["has_tools_parts"]:
            # Add tools and parts section to the answer
            tools_section = self._format_tools_parts_section()
            response["answer"] = response["answer"] + "\n\n" + tools_section
            response["tools_parts"] = self.tools_parts_data
            response["has_tools_parts"] = True
        else:
            response["tools_parts"] = None
            response["has_tools_parts"] = False
        
        return response
    
    def _format_tools_parts_section(self) -> str:
        """Format tools and parts as markdown section."""
        
        sections = []
        
        if self.tools_parts_data["tools"]:
            tools_list = "\n".join([f"- {tool}" for tool in self.tools_parts_data["tools"]])
            sections.append(f"**🔧 Tools Needed:**\n{tools_list}")
        
        if self.tools_parts_data["parts"]:
            parts_list = "\n".join([f"- {part}" for part in self.tools_parts_data["parts"]])
            sections.append(f"**🔩 Parts Required:**\n{parts_list}")
        
        if self.tools_parts_data["cost_estimates"]:
            cost_info = []
            for estimate in self.tools_parts_data["cost_estimates"]:
                cost_info.append(f"- {estimate['currency']} {estimate['amount']:.2f}")
            if cost_info:
                cost_list = "\n".join(cost_info)
                sections.append(f"**💰 Estimated Costs:**\n{cost_list}")
        
        if sections:
            return "---\n\n### 🛠️ Required Tools & Parts\n\n" + "\n\n".join(sections)
        
        return ""

# Global instances
tools_parts_extractor = ToolsPartsExtractor()
user_preference_service = UserPreferenceService()