import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from api.database.table_models import ServiceProvider
from api.models.service_provider import ServiceProviderCreate, ServiceProviderUpdate


class ServiceProviderRepository:
    """Repository for service provider operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, service_provider_data: ServiceProviderCreate) -> ServiceProvider:
        """Create a new service provider."""
        service_provider = ServiceProvider(
            id=uuid.uuid4(),
            **service_provider_data.model_dump()
        )
        self.db.add(service_provider)
        await self.db.commit()
        await self.db.refresh(service_provider)
        return service_provider
    
    async def get_by_id(self, provider_id: uuid.UUID) -> Optional[ServiceProvider]:
        """Get service provider by ID."""
        result = await self.db.execute(
            select(ServiceProvider).where(ServiceProvider.id == provider_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ServiceProvider]:
        """Get all service providers with pagination."""
        result = await self.db.execute(
            select(ServiceProvider)
            .offset(skip)
            .limit(limit)
            .order_by(ServiceProvider.rating.desc())
        )
        return result.scalars().all()
    
    async def get_by_specialty(self, specialty: str) -> List[ServiceProvider]:
        """Get service providers by specialty."""
        result = await self.db.execute(
            select(ServiceProvider).where(
                ServiceProvider.specialties.any(specialty)
            ).order_by(ServiceProvider.rating.desc())
        )
        return result.scalars().all()
    
    async def get_by_location(self, location: str) -> List[ServiceProvider]:
        """Get service providers by location."""
        result = await self.db.execute(
            select(ServiceProvider).where(
                ServiceProvider.location.ilike(f"%{location}%")
            ).order_by(ServiceProvider.rating.desc())
        )
        return result.scalars().all()
    
    async def get_best_rated(self, limit: int = 5) -> List[ServiceProvider]:
        """Get best rated service providers."""
        result = await self.db.execute(
            select(ServiceProvider)
            .where(ServiceProvider.rating > 0)
            .order_by(ServiceProvider.rating.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search(
        self, 
        specialty: Optional[str] = None,
        location: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_cost_per_hour: Optional[float] = None
    ) -> List[ServiceProvider]:
        """Search service providers with filters."""
        query = select(ServiceProvider)
        conditions = []
        
        if specialty:
            conditions.append(ServiceProvider.specialties.any(specialty))
        
        if location:
            conditions.append(ServiceProvider.location.ilike(f"%{location}%"))
        
        if min_rating is not None:
            conditions.append(ServiceProvider.rating >= min_rating)
        
        if max_cost_per_hour is not None:
            conditions.append(ServiceProvider.average_cost_per_hour <= max_cost_per_hour)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ServiceProvider.rating.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(
        self, 
        provider_id: uuid.UUID, 
        update_data: ServiceProviderUpdate
    ) -> Optional[ServiceProvider]:
        """Update service provider."""
        service_provider = await self.get_by_id(provider_id)
        if not service_provider:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(service_provider, field, value)
        
        await self.db.commit()
        await self.db.refresh(service_provider)
        return service_provider
    
    async def delete(self, provider_id: uuid.UUID) -> bool:
        """Delete service provider."""
        service_provider = await self.get_by_id(provider_id)
        if not service_provider:
            return False
        
        await self.db.delete(service_provider)
        await self.db.commit()
        return True