from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int
    customization: Optional[str] = None


class OrderCreate(BaseModel):
    order_type: str   # dine_in / take_away / delivery
    items: List[OrderItemCreate]

class GetOrders(BaseModel):
    order_id: Optional[int] = None
    order_status: Optional[str] = None
    order_type: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    page: Optional[int] = 1             
    limit: Optional[int] = 10  

class OrderStatus(BaseModel):
    order_id: Optional[int]
    status: Optional[str]
    payment_status: Optional[str]

class Menusearch(BaseModel):
    item_type: Optional[str] = None
    item_name: Optional[str] = None


class OrderResponse(BaseModel):
    success: bool
    message: str
    data: dict = {}
