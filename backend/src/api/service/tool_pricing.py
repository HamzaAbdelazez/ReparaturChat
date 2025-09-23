import logging
import asyncio
# import aiohttp
from typing import List, Dict
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.database.table_models import Tool, ToolPrice

logger = logging.getLogger(__name__)


class ToolPricingService:
    """Service for tool pricing and external API integration ."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def update_tool_prices(self, tool_id: UUID) -> List[Dict]:
        """Update tool prices from external sources."""
        try:
            # Get tool details
            tool_result = await self.db.execute(select(Tool).where(Tool.id == tool_id))
            tool = tool_result.scalar_one_or_none()
            
            if not tool:
                raise ValueError("Tool not found")
            
            # Simulate external API calls (in real implementation, use actual APIs)
            prices = await self._fetch_prices_from_apis(tool.name)
            
            # Update database
            for price_data in prices:
                tool_price = ToolPrice(
                    tool_id=tool_id,
                    vendor=price_data['vendor'],
                    price=price_data['price'],
                    url=price_data.get('url'),
                    last_updated=datetime.now(timezone.utc)
                )
                self.db.add(tool_price)
            
            await self.db.commit()
            
            # Update tool min/max prices
            await self._update_tool_price_range(tool_id)
            
            return prices
            
        except Exception as e:
            logger.error(f"Error updating tool prices: {e}")
            await self.db.rollback()
            raise
    
    async def _fetch_prices_from_apis(self, tool_name: str) -> List[Dict]:
        """Simulate fetching prices from external APIs."""
        # In a real implementation, you would call actual e-commerce APIs
        # For demo purposes, we'll simulate with mock data
        
        mock_prices = [
            {
                'vendor': 'Amazon',
                'price': 25.99,
                'url': f'https://amazon.de/search?q={tool_name.replace(" ", "+")}'
            },
            {
                'vendor': 'eBay',
                'price': 22.50,
                'url': f'https://ebay.de/search?q={tool_name.replace(" ", "+")}'
            },
            {
                'vendor': 'OBI',
                'price': 28.99,
                'url': f'https://obi.de/search?q={tool_name.replace(" ", "+")}'
            }
        ]
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        return mock_prices
    
    async def _update_tool_price_range(self, tool_id: UUID):
        """Update tool's min/max price based on current price data."""
        try:
            # Get all prices for this tool
            price_result = await self.db.execute(
                select(ToolPrice).where(ToolPrice.tool_id == tool_id)
            )
            prices = price_result.scalars().all()
            
            if not prices:
                return
            
            price_values = [p.price for p in prices]
            min_price = min(price_values)
            max_price = max(price_values)
            
            # Update tool
            tool_result = await self.db.execute(select(Tool).where(Tool.id == tool_id))
            tool = tool_result.scalar_one_or_none()
            
            if tool:
                tool.min_price = min_price
                tool.max_price = max_price
                await self.db.commit()
                
        except Exception as e:
            logger.error(f"Error updating tool price range: {e}")
            await self.db.rollback()
    
    async def get_tool_prices(self, tool_id: UUID) -> List[Dict]:
        """Get current tool prices from database."""
        try:
            price_result = await self.db.execute(
                select(ToolPrice).where(ToolPrice.tool_id == tool_id)
                .order_by(ToolPrice.price.asc())
            )
            prices = price_result.scalars().all()
            
            return [
                {
                    'vendor': p.vendor,
                    'price': p.price,
                    'url': p.url,
                    'last_updated': p.last_updated
                }
                for p in prices
            ]
            
        except Exception as e:
            logger.error(f"Error getting tool prices: {e}")
            return []
    
    async def get_cheapest_price(self, tool_id: UUID) -> Dict:
        """Get the cheapest price for a tool."""
        prices = await self.get_tool_prices(tool_id)
        
        if not prices:
            return {}
        
        return min(prices, key=lambda x: x['price'])
    
    async def compare_tool_prices(self, tool_ids: List[UUID]) -> Dict:
        """Compare prices across multiple tools."""
        comparison = {}
        
        for tool_id in tool_ids:
            tool_result = await self.db.execute(select(Tool).where(Tool.id == tool_id))
            tool = tool_result.scalar_one_or_none()
            
            if tool:
                prices = await self.get_tool_prices(tool_id)
                cheapest = await self.get_cheapest_price(tool_id)
                
                comparison[str(tool_id)] = {
                    'tool_name': tool.name,
                    'min_price': tool.min_price,
                    'max_price': tool.max_price,
                    'cheapest_vendor': cheapest.get('vendor'),
                    'cheapest_price': cheapest.get('price'),
                    'price_count': len(prices)
                }
        
        return comparison