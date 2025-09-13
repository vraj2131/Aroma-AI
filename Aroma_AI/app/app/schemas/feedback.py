from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ---- Input Schemas ----
class FeedbackBase(BaseModel):
    rating: int
    comments: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    order_id: int


class FeedbackUpdate(BaseModel):
    rating: Optional[int] = None
    comments: Optional[str] = None


# ---- Output Schema for Single Feedback ----
class FeedbackOut(BaseModel):
    id: int
    order_id: int
    rating: int
    comments: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


# ---- Response Wrappers ----
class FeedbackResponse(BaseModel):
    success: bool
    message: str
    data: Optional[FeedbackOut] = None


class FeedbackListResponse(BaseModel):
    success: bool
    message: str
    data: List[FeedbackOut] = []
