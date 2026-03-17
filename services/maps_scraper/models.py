from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

class MapsPlace(BaseModel):
    """
    Pydantic model for a Google Maps Place.
    Follows Strict Data Validation (CNS Rule 12).
    """
    place_id: str = Field(..., description="Unique identifier from Google Maps")
    name: str = Field(..., description="Business name")
    address: Optional[str] = Field(None, description="Full physical address")
    phone: Optional[str] = Field(None, description="Formatted phone number")
    website: Optional[str] = Field(None, description="Business website URL")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating (0-5)")
    review_count: Optional[int] = Field(0, ge=0, description="Total number of reviews")
    category: Optional[str] = Field(None, description="Business category (e.g., Restaurant)")
    latitude: Optional[float] = Field(None, description="GPS Latitude")
    longitude: Optional[float] = Field(None, description="GPS Longitude")
    plus_code: Optional[str] = Field(None, description="Google Plus Code")
    is_claimed: Optional[bool] = Field(None, description="Whether the business is claimed on Maps")
    
    # Metadata for tracking
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        populate_by_name = True
