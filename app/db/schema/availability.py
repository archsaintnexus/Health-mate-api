from datetime import datetime
from pydantic import BaseModel

class SlotOutput(BaseModel):
    id: int
    provider_id: int
    start_time: datetime
    end_time: datetime
    is_booked: bool

    class Config:
        from_attributes = True