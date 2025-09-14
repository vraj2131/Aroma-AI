from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class TableBooking(BaseModel):
    table_ids: List[int]
    booking_date_time: Optional[datetime]

class TableCancel(BaseModel):
    table_id: int
    status: Optional[str]

class TableFetch(BaseModel):
    status: Optional[str]

class TableResponse(BaseModel):
    success: bool
    message: str
    table_id: Optional[int] = None
