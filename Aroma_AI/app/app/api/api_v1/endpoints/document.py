import shutil
from fastapi import UploadFile, File
from logging import getLogger
import os
import shutil

from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
# from app.core.security import authentication
from app.models.user import User
from app import schemas
from app import crud
from app.api import deps



router = APIRouter()
_logger = getLogger("Document Logger")


@router.post('/upload/', response_model=schemas.UploadDocumentResponse)
def document_upload(file: UploadFile = File(...),current_user: User = Depends(deps.get_current_active_user) ,db: Session = Depends(deps.get_db),) -> JSONResponse:
    try:
        _logger.info("Document upload started for company")
        os.makedirs("./files", exist_ok=True)
        path = f"./files/{file.filename}"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_path = path
        response = crud.document.upload_document(db, current_user, file_path)
        return JSONResponse(
            status_code=200 if response.get("success") else 400, content={"success": response.get("success"),
                "errormsg": response.get("msg"), "data": response.get("data", {})
            },
        )
    except Exception as e:
            _logger.exception("Unexpected error in upload_document: %s", str(e))
            return JSONResponse(status_code=500, content={"success": False, "errormsg": "Internal server error"})


# @app.post("/save-file/")
# def save_file(file: UploadFile = File(...)):
#     path = f"tmp/genai/{file.filename}"
#     with open(path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     return {"file_path": path}