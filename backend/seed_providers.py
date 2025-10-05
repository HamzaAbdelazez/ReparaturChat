
"""
Simple script to seed service providers.
Run this from the backend directory: python seed_providers.py
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the seeding script
from api.scripts.seed_service_providers import seed_service_providers
import asyncio

if __name__ == "__main__":
    asyncio.run(seed_service_providers())