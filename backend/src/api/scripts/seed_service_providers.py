"""
Script to seed the database with initial service provider data.
Run this script to populate the service_providers table with sample data.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from api.routers.dependencies import async_session_maker
from api.database.repository.service_provider import ServiceProviderRepository
from api.models.service_provider import ServiceProviderCreate


async def seed_service_providers():
    """Seed the database with initial service provider data."""
    
    sample_providers = [
        ServiceProviderCreate(
            name="TechFix Pro",
            location="Berlin, Germany",
            specialties=["smartphone", "tablet", "laptop", "desktop computer"],
            average_cost_per_hour=45.0,
            average_repair_time_hours=1.5,
            rating=4.5,
            commission_rate=0.1,
            website_url="https://techfixpro.de"
        ),
        ServiceProviderCreate(
            name="ApplianceExperts",
            location="Munich, Germany", 
            specialties=["washing machine", "dishwasher", "refrigerator", "oven"],
            average_cost_per_hour=60.0,
            average_repair_time_hours=2.5,
            rating=4.2,
            commission_rate=0.15,
            website_url="https://applianceexperts.de"
        ),
        ServiceProviderCreate(
            name="ElectroFix Solutions",
            location="Hamburg, Germany",
            specialties=["television", "sound system", "gaming console", "smart home device"],
            average_cost_per_hour=55.0,
            average_repair_time_hours=2.0,
            rating=4.3,
            commission_rate=0.12,
            website_url="https://electrofix.de"
        ),
        ServiceProviderCreate(
            name="Quick Repair Service",
            location="Frankfurt, Germany",
            specialties=["smartphone", "laptop", "tablet"],
            average_cost_per_hour=40.0,
            average_repair_time_hours=1.0,
            rating=4.0,
            commission_rate=0.08,
            website_url="https://quickrepair.de"
        ),
        ServiceProviderCreate(
            name="HomeAppliance Masters",
            location="Cologne, Germany",
            specialties=["washing machine", "dryer", "refrigerator", "microwave"],
            average_cost_per_hour=65.0,
            average_repair_time_hours=3.0,
            rating=4.6,
            commission_rate=0.18,
            website_url="https://homeappliancemasters.de"
        ),
        ServiceProviderCreate(
            name="Mobile Device Clinic",
            location="Stuttgart, Germany",
            specialties=["smartphone", "tablet", "smartwatch", "headphones"],
            average_cost_per_hour=35.0,
            average_repair_time_hours=0.8,
            rating=4.1,
            commission_rate=0.07,
            website_url="https://mobiledeviceclinic.de"
        ),
        ServiceProviderCreate(
            name="Computer Rescue Team",
            location="Düsseldorf, Germany",
            specialties=["laptop", "desktop computer", "gaming pc", "server"],
            average_cost_per_hour=50.0,
            average_repair_time_hours=2.2,
            rating=4.4,
            commission_rate=0.11,
            website_url="https://computerrescue.de"
        ),
        ServiceProviderCreate(
            name="Audio Visual Experts",
            location="Leipzig, Germany",
            specialties=["television", "projector", "sound system", "camera"],
            average_cost_per_hour=58.0,
            average_repair_time_hours=2.8,
            rating=4.3,
            commission_rate=0.14,
            website_url="https://avexperts.de"
        ),
        ServiceProviderCreate(
            name="Smart Home Solutions",
            location="Dresden, Germany",
            specialties=["smart home device", "router", "smart tv", "security camera"],
            average_cost_per_hour=48.0,
            average_repair_time_hours=1.8,
            rating=4.2,
            commission_rate=0.10,
            website_url="https://smarthomesolutions.de"
        ),
        ServiceProviderCreate(
            name="Budget Repair Hub",
            location="Bremen, Germany",
            specialties=["smartphone", "laptop", "small appliance"],
            average_cost_per_hour=30.0,
            average_repair_time_hours=1.2,
            rating=3.8,
            commission_rate=0.05,
            website_url="https://budgetrepair.de"
        ),
        ServiceProviderCreate(
            name="Premium Tech Services",
            location="Hannover, Germany",
            specialties=["laptop", "smartphone", "tablet", "gaming console"],
            average_cost_per_hour=70.0,
            average_repair_time_hours=1.5,
            rating=4.7,
            commission_rate=0.20,
            website_url="https://premiumtech.de"
        ),
        ServiceProviderCreate(
            name="Kitchen Appliance Pro",
            location="Nuremberg, Germany",
            specialties=["oven", "microwave", "dishwasher", "coffee machine"],
            average_cost_per_hour=62.0,
            average_repair_time_hours=2.5,
            rating=4.4,
            commission_rate=0.16,
            website_url="https://kitchenappliancepro.de"
        )
    ]
    
    async with async_session_maker() as db:
        repo = ServiceProviderRepository(db)
        
        print("Seeding service providers...")
        created_count = 0
        
        for provider_data in sample_providers:
            try:
                # Check if provider already exists
                existing_providers = await repo.search(location=provider_data.location)
                provider_exists = any(p.name == provider_data.name for p in existing_providers)
                
                if not provider_exists:
                    provider = await repo.create(provider_data)
                    print(f"[SUCCESS] Created: {provider.name} in {provider.location}")
                    created_count += 1
                else:
                    print(f"[SKIP] Skipped: {provider_data.name} (already exists)")
                    
            except Exception as e:
                print(f"[ERROR] Error creating {provider_data.name}: {e}")
        
        print(f"\n[COMPLETE] Seeding completed! Created {created_count} new service providers.")
        
        # Display summary
        all_providers = await repo.get_all()
        print(f"[INFO] Total service providers in database: {len(all_providers)}")
        
        if all_providers:
            print("\n[SUMMARY] Service providers by location:")
            locations = {}
            for provider in all_providers:
                location = provider.location or "Unknown"
                locations[location] = locations.get(location, 0) + 1
            
            for location, count in sorted(locations.items()):
                print(f"   {location}: {count} provider(s)")


if __name__ == "__main__":
    print("[START] Starting service provider database seeding...")
    asyncio.run(seed_service_providers())
    print("[DONE] Seeding process completed!")