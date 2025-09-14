from typing import Optional,Literal,List,Dict
from pydantic import BaseModel
from fastapi import Form

class DeliveryStatus(BaseModel):
    order_id: int
    status: Literal['Assigned','Pending', 'Out for Delivery', 'Delivered', 'Cancelled']

class DeliveryDetails(BaseModel):
    order_id: Optional[int]

class DeliveryResponse(BaseModel):
    status: bool
    data: Optional[Dict]
    errormsg: Optional[str]