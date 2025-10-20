import uuid
from typing import List, Optional
from pydantic import BaseModel


class ServiceProviderBase(BaseModel):
    """Base model for service provider."""
    name: str
    location: Optional[str] = None
    specialties: Optional[List[str]] = None
    average_cost_per_hour: Optional[float] = None
    average_repair_time_hours: Optional[float] = None
    rating: Optional[float] = 0.0
    commission_rate: Optional[float] = 0.0
    website_url: Optional[str] = None


class ServiceProviderCreate(ServiceProviderBase):
    """Model for creating a service provider."""
    pass


class ServiceProviderUpdate(BaseModel):
    """Model for updating a service provider."""
    name: Optional[str] = None
    location: Optional[str] = None
    specialties: Optional[List[str]] = None
    average_cost_per_hour: Optional[float] = None
    average_repair_time_hours: Optional[float] = None
    rating: Optional[float] = None
    commission_rate: Optional[float] = None
    website_url: Optional[str] = None


class ServiceProviderRead(ServiceProviderBase):
    """Model for reading a service provider."""
    id: uuid.UUID

    class Config:
        from_attributes = True


class ServiceProviderQuote(BaseModel):
    """Model for service provider quote comparison."""
    provider_id: uuid.UUID
    provider_name: str
    estimated_cost: float
    estimated_time_hours: float
    rating: float
    specialties: List[str]
    location: Optional[str] = None
    website_url: Optional[str] = None