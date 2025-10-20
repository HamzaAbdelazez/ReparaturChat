import logging
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from api.routers.dependencies import db_dependency
from api.database.repository.service_provider import ServiceProviderRepository
from api.models.service_provider import (
    ServiceProviderCreate, 
    ServiceProviderRead, 
    ServiceProviderUpdate,
    ServiceProviderQuote
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/service-providers", tags=["service-providers"])


@router.post("/", response_model=ServiceProviderRead)
async def create_service_provider(
    provider_data: ServiceProviderCreate,
    db = Depends(db_dependency)
):
    """Create a new service provider."""
    try:
        repo = ServiceProviderRepository(db)
        provider = await repo.create(provider_data)
        return ServiceProviderRead.model_validate(provider)
    except Exception as e:
        logger.error(f"Error creating service provider: {e}")
        raise HTTPException(status_code=500, detail="Failed to create service provider")


@router.get("/", response_model=List[ServiceProviderRead])
async def get_service_providers(
    skip: int = Query(0, ge=0, description="Number of providers to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of providers to return"),
    db = Depends(db_dependency)
):
    """Get all service providers with pagination."""
    try:
        repo = ServiceProviderRepository(db)
        providers = await repo.get_all(skip=skip, limit=limit)
        return [ServiceProviderRead.model_validate(p) for p in providers]
    except Exception as e:
        logger.error(f"Error fetching service providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch service providers")


@router.get("/{provider_id}", response_model=ServiceProviderRead)
async def get_service_provider(
    provider_id: UUID,
    db = Depends(db_dependency)
):
    """Get service provider by ID."""
    try:
        repo = ServiceProviderRepository(db)
        provider = await repo.get_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Service provider not found")
        return ServiceProviderRead.model_validate(provider)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching service provider: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch service provider")


@router.put("/{provider_id}", response_model=ServiceProviderRead)
async def update_service_provider(
    provider_id: UUID,
    update_data: ServiceProviderUpdate,
    db = Depends(db_dependency)
):
    """Update service provider."""
    try:
        repo = ServiceProviderRepository(db)
        provider = await repo.update(provider_id, update_data)
        if not provider:
            raise HTTPException(status_code=404, detail="Service provider not found")
        return ServiceProviderRead.model_validate(provider)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service provider: {e}")
        raise HTTPException(status_code=500, detail="Failed to update service provider")


@router.delete("/{provider_id}")
async def delete_service_provider(
    provider_id: UUID,
    db = Depends(db_dependency)
):
    """Delete service provider."""
    try:
        repo = ServiceProviderRepository(db)
        deleted = await repo.delete(provider_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Service provider not found")
        return {"message": "Service provider deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting service provider: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete service provider")


@router.get("/search/by-specialty", response_model=List[ServiceProviderRead])
async def get_providers_by_specialty(
    specialty: str = Query(..., description="Specialty to search for"),
    db = Depends(db_dependency)
):
    """Get service providers by specialty."""
    try:
        repo = ServiceProviderRepository(db)
        providers = await repo.get_by_specialty(specialty)
        return [ServiceProviderRead.model_validate(p) for p in providers]
    except Exception as e:
        logger.error(f"Error searching providers by specialty: {e}")
        raise HTTPException(status_code=500, detail="Failed to search providers")


@router.get("/search/by-location", response_model=List[ServiceProviderRead])
async def get_providers_by_location(
    location: str = Query(..., description="Location to search for"),
    db = Depends(db_dependency)
):
    """Get service providers by location."""
    try:
        repo = ServiceProviderRepository(db)
        providers = await repo.get_by_location(location)
        return [ServiceProviderRead.model_validate(p) for p in providers]
    except Exception as e:
        logger.error(f"Error searching providers by location: {e}")
        raise HTTPException(status_code=500, detail="Failed to search providers")


@router.get("/search/best-rated", response_model=List[ServiceProviderRead])
async def get_best_rated_providers(
    limit: int = Query(5, ge=1, le=50, description="Number of top providers to return"),
    db = Depends(db_dependency)
):
    """Get best rated service providers."""
    try:
        repo = ServiceProviderRepository(db)
        providers = await repo.get_best_rated(limit=limit)
        return [ServiceProviderRead.model_validate(p) for p in providers]
    except Exception as e:
        logger.error(f"Error fetching best rated providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch best rated providers")


@router.get("/search/advanced", response_model=List[ServiceProviderRead])
async def search_providers(
    specialty: Optional[str] = Query(None, description="Specialty filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    max_cost_per_hour: Optional[float] = Query(None, ge=0, description="Maximum cost per hour"),
    db = Depends(db_dependency)
):
    """Advanced search for service providers."""
    try:
        repo = ServiceProviderRepository(db)
        providers = await repo.search(
            specialty=specialty,
            location=location,
            min_rating=min_rating,
            max_cost_per_hour=max_cost_per_hour
        )
        return [ServiceProviderRead.model_validate(p) for p in providers]
    except Exception as e:
        logger.error(f"Error in advanced search: {e}")
        raise HTTPException(status_code=500, detail="Failed to search providers")


@router.get("/quotes/compare", response_model=List[ServiceProviderQuote])
async def get_provider_quotes(
    device_category: Optional[str] = Query(None, description="Device category for specialized providers"),
    location: Optional[str] = Query(None, description="User location for nearby providers"),
    max_providers: int = Query(3, ge=1, le=10, description="Maximum number of quotes to return"),
    db = Depends(db_dependency)
):
    """Get quotes from multiple service providers for comparison."""
    try:
        repo = ServiceProviderRepository(db)
        
        # Search for relevant providers
        providers = await repo.search(
            specialty=device_category,
            location=location,
            min_rating=3.0  # Only include decent rated providers
        )
        
        # Limit to requested number
        providers = providers[:max_providers]
        
        quotes = []
        for provider in providers:
            # Calculate estimated cost and time
            base_cost = provider.average_cost_per_hour or 50.0
            base_time = provider.average_repair_time_hours or 2.0
            
            # Add some variation based on rating (higher rated = slightly higher cost)
            cost_multiplier = 1.0 + ((provider.rating - 3.0) * 0.1) if provider.rating else 1.0
            estimated_cost = base_cost * base_time * cost_multiplier
            
            quote = ServiceProviderQuote(
                provider_id=provider.id,
                provider_name=provider.name,
                estimated_cost=round(estimated_cost, 2),
                estimated_time_hours=base_time,
                rating=provider.rating or 0.0,
                specialties=provider.specialties or [],
                location=provider.location,
                website_url=provider.website_url
            )
            quotes.append(quote)
        
        # Sort by cost (cheapest first)
        quotes.sort(key=lambda x: x.estimated_cost)
        
        return quotes
        
    except Exception as e:
        logger.error(f"Error getting provider quotes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get provider quotes")