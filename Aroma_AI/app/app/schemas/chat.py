from pydantic import BaseModel
from typing import Optional, List

class AskQna(BaseModel):
    query: str


class ChatState(BaseModel):
    session_id: str
    state: dict

class QnaResponse(BaseModel):
    status: bool
    data: Optional[ChatState]
    errormsg: Optional[str]

class ContinueChatRequest(BaseModel):
    session_id: str
    query: str