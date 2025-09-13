from typing import Optional,Literal,List,Dict
from pydantic import BaseModel
from fastapi import Form


class UploadDocumentRequest(BaseModel):
    file_path: Optional[str] = "" 
    document_id: int
    module: int
    doc_access_type: int
    company_id: int
    user_ids: List[int]

    @classmethod
    def as_form(
        cls,
        file_path: str = Form(""),
        document_id: int = Form(...),
        module: int = Form(...),
        doc_access_type: int = Form(...),       
        company_id: int = Form(...),
        user_ids: List[int] = Form([]),
    ):
        return cls(
            file_path=file_path,
            document_id=document_id,
            module=module,
            doc_access_type=doc_access_type,
            company_id=company_id,
            user_ids=user_ids
        )
class UploadDocumentResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    errormsg: Optional[str] = None