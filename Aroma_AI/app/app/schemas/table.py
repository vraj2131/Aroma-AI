from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class TableBooking(BaseModel):
    table_id: int
    booking_date_time: datetime

class TableCancel(BaseModel):
    table_id: int

class TableResponse(BaseModel):
    success: bool
    message: str
    table_id: Optional[int] = None