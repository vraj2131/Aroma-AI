import shutil
from fastapi import UploadFile, File
from logging import getLogger
import os
import shutil
import json

from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
# from app.core.security import authentication
from app.models.user import User
from app import schemas
from app import crud
from app.api import deps



router = APIRouter()
_logger = getLogger("Chat Logger")


@router.post('/Message/', response_model=schemas.QnaResponse)
async def chat_responce(*,db: Session = Depends(deps.get_db), params: schemas.AskQna,
                  current_user:User = Depends(deps.get_current_active_user)) -> JSONResponse:
    # try:
    response = await crud.qna.ask_qna(db, current_user, params)
    _logger.info("Ask Qna Response : %r" % response)
    return JSONResponse(status_code=200 if response.get('success') else 400,
                        content={'success': response.get('success'), "errormsg": response.get('msg'),
                                    'data': response.get('data')})
    # except Exception as e:
    #     _logger.error("Exception in Ask Qna: %s" % e)
    #     return JSONResponse(status_code=400, content={'success': False, "errormsg": str(e)})