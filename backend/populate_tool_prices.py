"""
Script to populate tool prices in the database.
Run this script to fix null tool prices issue.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
backend_src = Path(__file__).parent / "src"
sys.path.append(str(backend_src))

from api.config.db import get_database_url, create_async_engine
from api.database.table_models import Tool, ToolPrice
from api.service.tool_pricing import ToolPricingService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone


async def populate_tool_prices():
    """Populate tool prices for all existing tools."""
    
    print("🔧 Starting tool price population...")
    
    # Create database connection
    engine = create_async_engine(get_database_url())
    
    try:
        async with AsyncSession(engine) as session:
            # Get all tools that don't have prices
            result = await session.execute(
                select(Tool).where(
                    (Tool.min_price.is_(None)) | (Tool.max_price.is_(None))
                )
            )
            tools = result.scalars().all()
            
            if not tools:
                print("✅ All tools already have prices!")
                return
            
            print(f"📊 Found {len(tools)} tools without prices. Updating...")
            
            # Initialize pricing service
            pricing_service = ToolPricingService(session)
            
            # Update prices for each tool
            for i, tool in enumerate(tools, 1):
                print(f"🔄 [{i}/{len(tools)}] Updating prices for: {tool.name}")
                
                try:
                    # Update tool prices
                    prices = await pricing_service.update_tool_prices(tool.id)
                    print(f"   ✅ Added {len(prices)} price entries")
                    
                except Exception as e:
                    print(f"   ❌ Error updating {tool.name}: {e}")
                    continue
            
            print("✅ Tool price population completed!")
            
            # Show summary
            await show_price_summary(session)
            
    except Exception as e:
        print(f"❌ Error during price population: {e}")
        
    finally:
        await engine.dispose()


async def show_price_summary(session: AsyncSession):
    """Show a summary of tool prices."""
    
    print("\n📈 PRICE SUMMARY:")
    print("-" * 50)
    
    # Get tools with prices
    result = await session.execute(
        select(Tool).where(Tool.min_price.isnot(None))
    )
    tools_with_prices = result.scalars().all()
    
    # Get total price entries
    result = await session.execute(select(ToolPrice))
    price_entries = result.scalars().all()
    
    print(f"🔧 Tools with prices: {len(tools_with_prices)}")
    print(f"💰 Total price entries: {len(price_entries)}")
    
    if tools_with_prices:
        print("\n🏷️  SAMPLE PRICES:")
        for tool in tools_with_prices[:5]:  # Show first 5
            print(f"   {tool.name}: €{tool.min_price:.2f} - €{tool.max_price:.2f}")
    
    print("-" * 50)


async def add_sample_tools():
    """Add some sample tools if none exist."""
    
    engine = create_async_engine(get_database_url())
    
    async with AsyncSession(engine) as session:
        # Check if tools exist
        result = await session.execute(select(Tool))
        existing_tools = result.scalars().all()
        
        if existing_tools:
            print(f"✅ Found {len(existing_tools)} existing tools")
            return
        
        print("➕ No tools found. Adding sample tools...")
        
        sample_tools = [
            {
                "name": "Screwdriver Set",
                "description": "Professional screwdriver set with multiple bits",
                "category": "Hand Tools",
                "reusability_score": 5
            },
            {
                "name": "Drill Bits Set",
                "description": "High-speed steel drill bits for various materials",
                "category": "Power Tool Accessories",
                "reusability_score": 4
            },
            {
                "name": "Multimeter",
                "description": "Digital multimeter for electrical measurements",
                "category": "Electronic Tools",
                "reusability_score": 5
            },
            {
                "name": "Socket Wrench Set",
                "description": "Metric and imperial socket wrench set",
                "category": "Hand Tools",
                "reusability_score": 5
            },
            {
                "name": "Soldering Iron",
                "description": "Temperature-controlled soldering iron",
                "category": "Electronic Tools",
                "reusability_score": 5
            }
        ]
        
        for tool_data in sample_tools:
            tool = Tool(**tool_data)
            session.add(tool)
        
        await session.commit()
        print(f"✅ Added {len(sample_tools)} sample tools")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🚀 Tool Price Populator")
    print("=" * 50)
    
    async def main():
        # First add sample tools if needed
        await add_sample_tools()
        
        # Then populate prices
        await populate_tool_prices()
    
    asyncio.run(main())