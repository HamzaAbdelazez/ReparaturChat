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
        """Extract cost estimates from text with associated items."""
        
        # Enhanced patterns to capture item names with their costs
        item_cost_patterns = [
            r'([^:\n\.]+?)[\s:]+\$(\d+(?:\.\d{2})?(?:\s*[-–]\s*\$?\d+(?:\.\d{2})?)?)',  # Item: $15-20 or Item $15
            r'([^:\n\.]+?)[\s:]+€(\d+(?:\.\d{2})?(?:\s*[-–]\s*€?\d+(?:\.\d{2})?)?)',   # Item: €15-20 or Item €15
            r'([^:\n\.]+?)[\s:]+(\d+(?:\.\d{2})?(?:\s*[-–]\s*\d+(?:\.\d{2})?)?) ?(?:dollars?|USD)',  # Item: 15 dollars
        ]
        
        estimates = []
        
        # Try to match items with their costs
        for pattern in item_cost_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    item_name = match[0].strip().strip('*-•').strip()
                    cost_str = match[1].strip()
                    
                    # Skip if item name is too short or generic
                    if len(item_name) < 3 or item_name.lower() in ['total', 'cost', 'price', 'estimate']:
                        continue
                    
                    # Parse cost range (e.g., "15-20" or "15")
                    if '-' in cost_str or '–' in cost_str:
                        # Handle ranges like "$15-20" or "15-20"
                        cost_parts = re.split(r'[-–]', cost_str)
                        if len(cost_parts) == 2:
                            min_cost = float(re.findall(r'\d+(?:\.\d{2})?', cost_parts[0])[0])
                            max_cost = float(re.findall(r'\d+(?:\.\d{2})?', cost_parts[1])[0])
                            cost_display = f"${min_cost:.0f}-${max_cost:.0f}"
                        else:
                            amount = float(re.findall(r'\d+(?:\.\d{2})?', cost_str)[0])
                            cost_display = f"${amount:.0f}"
                    else:
                        amount = float(re.findall(r'\d+(?:\.\d{2})?', cost_str)[0])
                        cost_display = f"${amount:.0f}"
                    
                    estimates.append({
                        "item": item_name,
                        "cost_display": cost_display,
                        "currency": "USD"
                    })
                except (ValueError, IndexError):
                    continue
        
        # If no item-cost pairs found, fallback to simple cost extraction
        if not estimates:
            simple_patterns = [
                r'\$(\d+(?:\.\d{2})?(?:\s*[-–]\s*\$?\d+(?:\.\d{2})?)?)',  # $15-20 or $15
                r'€(\d+(?:\.\d{2})?(?:\s*[-–]\s*€?\d+(?:\.\d{2})?)?)',   # €15-20 or €15
            ]
            
            for pattern in simple_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        cost_str = match.strip()
                        if '-' in cost_str or '–' in cost_str:
                            cost_display = cost_str
                        else:
                            amount = float(cost_str)
                            cost_display = f"${amount:.0f}"
                        
                        estimates.append({
                            "item": "General cost",
                            "cost_display": cost_display,
                            "currency": "USD"
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
        """Format tools and parts as markdown section with associated costs."""
        
        sections = []
        cost_estimates = self.tools_parts_data.get("cost_estimates", [])
        
        # Helper function to find cost for an item
        def find_cost_for_item(item_name: str) -> str:
            item_lower = item_name.lower()
            for estimate in cost_estimates:
                estimate_item = estimate.get("item", "").lower()
                # Check if the item name is mentioned in the cost estimate
                if any(word in estimate_item for word in item_lower.split()) or \
                   any(word in item_lower for word in estimate_item.split()):
                    return f" - **{estimate['cost_display']}**"
            return ""
        
        # Format tools with their costs
        if self.tools_parts_data["tools"]:
            tools_list = []
            for tool in self.tools_parts_data["tools"]:
                cost_info = find_cost_for_item(tool)
                tools_list.append(f"- {tool}{cost_info}")
            sections.append(f"**🔧 Tools Needed:**\n" + "\n".join(tools_list))
        
        # Format parts with their costs
        if self.tools_parts_data["parts"]:
            parts_list = []
            for part in self.tools_parts_data["parts"]:
                cost_info = find_cost_for_item(part)
                parts_list.append(f"- {part}{cost_info}")
            sections.append(f"**🔩 Parts Required:**\n" + "\n".join(parts_list))
        
        # Add any remaining cost estimates that weren't matched to tools/parts
        if cost_estimates:
            matched_items = set()
            # Track which cost estimates were already associated with tools/parts
            for tool in self.tools_parts_data.get("tools", []):
                for estimate in cost_estimates:
                    estimate_item = estimate.get("item", "").lower()
                    if any(word in estimate_item for word in tool.lower().split()) or \
                       any(word in tool.lower() for word in estimate_item.split()):
                        matched_items.add(estimate.get("item", ""))
            
            for part in self.tools_parts_data.get("parts", []):
                for estimate in cost_estimates:
                    estimate_item = estimate.get("item", "").lower()
                    if any(word in estimate_item for word in part.lower().split()) or \
                       any(word in part.lower() for word in estimate_item.split()):
                        matched_items.add(estimate.get("item", ""))
            
            # Add unmatched cost estimates
            unmatched_costs = []
            for estimate in cost_estimates:
                if estimate.get("item", "") not in matched_items:
                    unmatched_costs.append(f"- {estimate['item']}: **{estimate['cost_display']}**")
            
            if unmatched_costs:
                sections.append(f"**💰 Additional Costs:**\n" + "\n".join(unmatched_costs))
        
        if sections:
            return "---\n\n### 🛠️ Required Tools & Parts\n\n" + "\n\n".join(sections)
        
        return ""

# Global instances
tools_parts_extractor = ToolsPartsExtractor()
user_preference_service = UserPreferenceService()