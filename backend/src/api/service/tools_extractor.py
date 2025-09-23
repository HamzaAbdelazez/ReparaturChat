import re
from typing import List, Dict

def extract_tools_from_text(text: str) -> List[str]:
    """
    Extract tool names from a PDF text.
    Looks for sections like 'Tools Required:' or bullet lists.
    """
    tools = []
    
    # Look for "Tools Required:" section
    pattern = r"(tools?\s+required[:\-]?\s*)([\s\S]+?)(?:\n\s*\n|repair\s+steps|instructions|procedure|\Z)"
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        section = match.group(2)
        for line in section.splitlines():
            # Clean the line - remove bullet points and leading/trailing whitespace
            cleaned_line = line.strip()
            # Remove bullet points and dashes from the beginning
            cleaned_line = re.sub(r'^[\s•\-–—\*\+\.\d]*\s*', '', cleaned_line)
            # Remove trailing punctuation
            cleaned_line = cleaned_line.strip('.:;,-')
            
            # Validate tool name - must be substantial and meaningful
            if not _is_valid_tool_name(cleaned_line):
                continue
            
            # Skip lines that look like steps/instructions
            if any(word in cleaned_line.lower() for word in ['step', 'instruction', 'procedure', 'use', 'remove', 'install', 'test']):
                continue
            
            tools.append(cleaned_line)
    
    # Also look for standalone tool mentions in bullet points
    bullet_pattern = r"^[\s]*[•\-–—\*\+]\s*([^:]+?)(?:\s*$|\s*[\-–])"
    for line in text.splitlines():
        match = re.match(bullet_pattern, line, re.MULTILINE)
        if match:
            tool_candidate = match.group(1).strip()
            tool_candidate = tool_candidate.strip('.:;,-')
            
            if (_is_valid_tool_name(tool_candidate) and 
                not any(word in tool_candidate.lower() for word in ['step', 'use', 'remove', 'install', 'test']) and
                tool_candidate not in tools):
                tools.append(tool_candidate)
    
    # Filter out duplicates and return clean list
    return list(set([tool for tool in tools if _is_valid_tool_name(tool)]))

def _is_valid_tool_name(name: str) -> bool:
    """
    Validate if a string is a valid tool name.
    """
    if not name or not name.strip():
        return False
    
    name = name.strip()
    
    # Must have at least 2 characters and contain letters
    if len(name) < 2 or not re.search(r'[a-zA-Z]', name):
        return False
    
    # Skip if it's only special characters, numbers, or dashes
    if re.match(r'^[\W\d\-–—\s]*$', name):
        return False
    
    # Skip if it's only dashes/punctuation
    if re.match(r'^[\-–—\s\.,:;]*$', name):
        return False
    
    # Skip if too long (likely a description)
    if len(name.split()) > 4:
        return False
    
    # Skip common non-tool words and action phrases
    non_tool_patterns = [
        r'\bempty\b.*\bpockets\b',
        r'\bremove\b.*\bfrom\b',
        r'\bdisconnect\b.*\bfrom\b',
        r'\bunplug\b.*\bfrom\b',
        r'\bturn\s+off\b',
        r'\bswitch\s+off\b',
        r'\bstep\s+\d+',
        r'^\d+\.',
        r'\bcheck\s+that\b',
        r'\bmake\s+sure\b',
        r'\benzure\s+that\b',
        r'\(.*damaged.*\)',
        r'\(.*text.*\)',
        r'\(.*missing.*\)',
        r'\(.*unclear.*\)',
    ]
    
    name_lower = name.lower()
    for pattern in non_tool_patterns:
        if re.search(pattern, name_lower):
            return False
    
    # Skip common non-tool words
    non_tool_words = ['required', 'needed', 'parts', 'tools', 'steps', 'procedure', 'instructions', 
                      'empty', 'pockets', 'activate', 'activated', 'deactivate', 'deactivated',
                      'disconnect', 'unplug', 'remove', 'check', 'verify', 'ensure', 'turn',
                      'switch', 'press', 'hold', 'wait', 'note', 'warning', 'caution']
    if name_lower in non_tool_words:
        return False
    
    # Skip if it contains common action verbs that indicate it's an instruction, not a tool
    action_verbs = ['empty', 'remove', 'disconnect', 'unplug', 'turn', 'switch', 'press', 'hold',
                   'check', 'verify', 'ensure', 'make', 'take', 'put', 'place', 'position']
    words = name_lower.split()
    if len(words) > 1 and words[0] in action_verbs:
        return False
    
    return True

def get_tool_details(tool_name: str) -> Dict:
    """
    Generate tool details based on tool name.
    Returns description and estimated reusability score.
    """
    # Clean tool name
    clean_name = tool_name.strip().lower()
    
    # Tool categories and details mapping
    tool_details = {
        # Basic hand tools
        "screwdriver": {
            "description": "Essential tool for removing and installing screws",
            "reusability_score": 5,
            "category": "basic"
        },
        "phillips screwdriver": {
            "description": "Cross-head screwdriver for Phillips screws",
            "reusability_score": 5,
            "category": "basic"
        },
        "flathead screwdriver": {
            "description": "Flat-tip screwdriver for slotted screws",
            "reusability_score": 5,
            "category": "basic"
        },
        "wrench": {
            "description": "Tool for gripping and turning nuts and bolts",
            "reusability_score": 5,
            "category": "basic"
        },
        "pliers": {
            "description": "Tool for gripping, pulling, and cutting wires",
            "reusability_score": 5,
            "category": "basic"
        },
        "hammer": {
            "description": "Tool for striking and removing parts",
            "reusability_score": 4,
            "category": "basic"
        },
        
        # Electrical tools
        "multimeter": {
            "description": "Electronic measuring instrument for voltage, current, and resistance",
            "reusability_score": 5,
            "category": "electrical"
        },
        "soldering iron": {
            "description": "Tool for joining electrical components with solder",
            "reusability_score": 4,
            "category": "electrical"
        },
        "wire strippers": {
            "description": "Tool for removing insulation from electrical wires",
            "reusability_score": 5,
            "category": "electrical"
        },
        
        # Specialized tools
        "torx screwdriver": {
            "description": "Star-shaped screwdriver for Torx screws",
            "reusability_score": 4,
            "category": "specialized"
        },
        "hex key": {
            "description": "L-shaped tool for hexagonal socket screws",
            "reusability_score": 5,
            "category": "basic"
        },
        "allen key": {
            "description": "L-shaped tool for hexagonal socket screws (hex key)",
            "reusability_score": 5,
            "category": "basic"
        },
        "spudger": {
            "description": "Non-conductive tool for safely prying electronic components",
            "reusability_score": 4,
            "category": "specialized"
        },
        "plastic pry tools": {
            "description": "Set of plastic tools for opening device cases without damage",
            "reusability_score": 4,
            "category": "specialized"
        }
    }
    
    # Try to match tool name with known tools
    for known_tool, details in tool_details.items():
        if known_tool in clean_name or clean_name in known_tool:
            return details
    
    # Default for unknown tools
    return {
        "description": f"Repair tool: {tool_name}",
        "reusability_score": 3,
        "category": "general"
    }
