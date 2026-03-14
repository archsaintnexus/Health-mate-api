from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from db.schema.availability import SlotOutput
from db.schema.provider import ProviderOutput


# This is used when the user 
class AppointmentCreate(BaseModel):
  provider_id: int
  slot_id: int
  reason: Optional[str] = None
  notes: Optional[str] = None


class AppointmentOutput(BaseModel):
    id: int
    user_id: int
    provider_id: int
    slot_id: int
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: str
    created_at: datetime
    provider: ProviderOutput
    slot: SlotOutput

    class Config:
        from_attributes = True

