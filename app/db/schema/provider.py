from typing import Optional
from pydantic import BaseModel


class ProviderOutput(BaseModel):
    id: int
    full_name: str
    specialty: str
    location: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    rating: float
    years_exp: int
    is_active: bool

    class Config:
        from_attributes = True