"""
Device name extraction service.
Extracts device names and models from text content (PDFs, chat messages).
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from api.database.table_models import Device

logger = logging.getLogger(__name__)


class DeviceExtractorService:
    """Service for extracting device names from text content."""
    
    # Common device patterns and keywords
    DEVICE_PATTERNS = {
        'washing_machine': {
            'brands': ['bosch', 'siemens', 'miele', 'samsung', 'lg', 'whirlpool', 'electrolux', 'aeg'],
            'keywords': ['washing machine', 'washer', 'waschmaschine', 'front loader', 'top loader'],
            'model_patterns': [
                r'\b(bosch)\s*([a-z]+\d+)\b',
                r'\b(miele)\s*([a-z]+\d+)\b',
                r'\b(samsung)\s*(ww\d+[a-z]+)\b'
            ]
        },
        'dishwasher': {
            'brands': ['bosch', 'siemens', 'miele', 'samsung', 'lg', 'whirlpool', 'electrolux', 'aeg'],
            'keywords': ['dishwasher', 'spülmaschine', 'geschirrspüler'],
            'model_patterns': [
                r'\b(bosch)\s*([a-z]+\d+)\b',
                r'\b(miele)\s*([a-z]+\d+)\b'
            ]
        }
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def extract_device_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract device information from text content.
        
        Args:
            text: Text content (from PDF or chat)
            
        Returns:
            Dict with device info or None if no device found
        """
        try:
            text_lower = text.lower()
            
            # Try to find devices using patterns
            detected_devices = []
            
            for category, category_data in self.DEVICE_PATTERNS.items():
                device_info = self._extract_device_by_category(text_lower, category, category_data)
                if device_info:
                    detected_devices.append({
                        'category': category,
                        'confidence': device_info['confidence'],
                        **device_info
                    })
            
            if not detected_devices:
                return None
            
            # Sort by confidence and return the best match
            detected_devices.sort(key=lambda x: x['confidence'], reverse=True)
            best_match = detected_devices[0]
            
            # Try to find matching device in database
            db_device = await self._find_device_in_database(best_match)
            
            if db_device:
                return {
                    'device_id': db_device.id,
                    'manufacturer': db_device.manufacturer,
                    'model': db_device.model,
                    'category': db_device.category,
                    'source': 'database_match',
                    'confidence': best_match['confidence'],
                    'extracted_text': best_match.get('full_match', '')
                }
            else:
                # Create device info from extracted data
                return {
                    'device_id': None,
                    'manufacturer': best_match.get('brand', '').title(),
                    'model': best_match.get('model', '').upper(),
                    'category': category.replace('_', ' ').title(),
                    'source': 'text_extraction',
                    'confidence': best_match['confidence'],
                    'extracted_text': best_match.get('full_match', '')
                }
                
        except Exception as e:
            logger.error(f"Error extracting device from text: {e}")
            return None
    
    def _extract_device_by_category(self, text: str, category: str, category_data: Dict) -> Optional[Dict]:
        """Extract device info for a specific category."""
        confidence = 0
        device_info = {}
        
        # Check for category keywords
        keyword_matches = sum(1 for keyword in category_data['keywords'] if keyword in text)
        if keyword_matches > 0:
            confidence += keyword_matches * 20
        
        # Check for brand mentions
        brand_matches = []
        for brand in category_data['brands']:
            if brand in text:
                brand_matches.append(brand)
                confidence += 30
        
        if not brand_matches and keyword_matches == 0:
            return None
        
        # Try to extract specific model using patterns
        model_info = None
        for pattern in category_data.get('model_patterns', []):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                model_info = {
                    'brand': match.group(1),
                    'model': ' '.join(filter(None, match.groups()[1:])),
                    'full_match': match.group(0)
                }
                confidence += 40
                break
        
        # If no specific model pattern, use the first brand found
        if not model_info and brand_matches:
            # Try to find model near the brand
            for brand in brand_matches:
                model = self._extract_model_near_brand(text, brand)
                model_info = {
                    'brand': brand,
                    'model': model or '',
                    'full_match': f"{brand} {model}" if model else brand
                }
                break
        
        if confidence < 20:  # Minimum confidence threshold
            return None
        
        return {
            'confidence': min(confidence, 100),
            'brand': model_info['brand'] if model_info else (brand_matches[0] if brand_matches else ''),
            'model': model_info['model'] if model_info else '',
            'full_match': model_info['full_match'] if model_info else ''
        }
    
    def _extract_model_near_brand(self, text: str, brand: str) -> Optional[str]:
        """Extract model name near a brand mention."""
        try:
            # Look for alphanumeric sequences near the brand
            brand_pattern = rf'\b{re.escape(brand)}\b'
            match = re.search(brand_pattern, text, re.IGNORECASE)
            
            if match:
                start_pos = match.end()
                # Look for model in the next 50 characters
                following_text = text[start_pos:start_pos + 50]
                
                # Pattern for common model formats
                model_patterns = [
                    r'\s+([A-Z0-9]{2,10}(?:[-\s][A-Z0-9]{1,5})?)',  # ABCD123, AB-123
                    r'\s+(\d+[A-Z]*(?:[-\s]\d+[A-Z]*)?)',  # 123A, 123-456
                    r'\s+(pro|air|max|plus|mini|ultra)\s*(\d+)?',  # Pro, Air 13, etc.
                ]
                
                for pattern in model_patterns:
                    model_match = re.search(pattern, following_text, re.IGNORECASE)
                    if model_match:
                        return model_match.group(1).strip()
            
            return None
        except Exception:
            return None
    
    async def _find_device_in_database(self, device_info: Dict) -> Optional[Device]:
        """Find matching device in database."""
        try:
            brand = device_info.get('brand', '').lower()
            model = device_info.get('model', '').lower()
            
            if not brand:
                return None
            
            # Search for device by manufacturer and model
            query = select(Device).where(
                and_(
                    Device.manufacturer.ilike(f'%{brand}%'),
                    or_(
                        Device.model.ilike(f'%{model}%') if model else False,
                        Device.model.ilike(f'{brand}%') if not model else False
                    )
                )
            )
            
            result = await self.db.execute(query)
            devices = result.scalars().all()
            
            if devices:
                # Return the first match (could be enhanced with better matching logic)
                return devices[0]
            
            # If no exact match, try broader search
            if model:
                query = select(Device).where(
                    or_(
                        Device.manufacturer.ilike(f'%{brand}%'),
                        Device.model.ilike(f'%{model}%')
                    )
                )
                result = await self.db.execute(query)
                devices = result.scalars().all()
                
                if devices:
                    return devices[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding device in database: {e}")
            return None
    
    async def extract_device_from_pdf_content(self, document_id: UUID) -> Optional[Dict]:
        """Extract device from PDF document chunks."""
        try:
            from api.database.table_models import DocumentChunk
            
            # Get document chunks
            query = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
            result = await self.db.execute(query)
            chunks = result.scalars().all()
            
            if not chunks:
                return None
            
            # Combine text from first few chunks (most likely to contain device info)
            combined_text = ' '.join([chunk.content for chunk in chunks[:5]])
            
            return await self.extract_device_from_text(combined_text)
            
        except Exception as e:
            logger.error(f"Error extracting device from PDF: {e}")
            return None
    
    def extract_device_from_chat_history(self, chat_history: List[Dict]) -> Optional[Dict]:
        """Extract device from chat conversation."""
        try:
            # Combine recent chat messages
            text_parts = []
            for message in chat_history[-10:]:  # Last 10 messages
                if message.get('type') == 'user' and message.get('content'):
                    text_parts.append(message['content'])
            
            if not text_parts:
                return None
            
            combined_text = ' '.join(text_parts)
            
            # This needs to be called with async context, so we'll return the text for processing
            return {'text_to_process': combined_text}
            
        except Exception as e:
            logger.error(f"Error extracting device from chat: {e}")
            return None