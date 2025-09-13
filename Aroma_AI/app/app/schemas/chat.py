from pydantic import BaseModel
from typing import Optional, List

class AskQna(BaseModel):
    query: str
    isnew: bool

class QnaResponse(BaseModel):
    status: bool
    data: Optional[list]
    errormsg: Optional[str]