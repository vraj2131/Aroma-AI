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
    try:
        response = await crud.qna.ask_qna(db, current_user, params)
        _logger.info("Ask Qna Response : %r" % response)
        return JSONResponse(status_code=200 if response.get('success') else 400,
                            content={'success': response.get('success'), "errormsg": response.get('msg'),
                                        'data': response.get('data')})
    except Exception as e:
        _logger.error("Exception in Ask Qna: %s" % e)
        return JSONResponse(status_code=400, content={'success': False, "errormsg": str(e)})

# @app.post("/save-file/")
# def save_file(file: UploadFile = File(...)):
#     path = f"tmp/genai/{file.filename}"
#     with open(path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     return {"file_path": path}

@router.post("/start_chat/", response_model=schemas.QnaResponse)
async def start_chat(
    *,
    db: Session = Depends(deps.get_db),
    params: schemas.AskQna,
    current_user: User = Depends(deps.get_current_active_user)
):
    session_id, state = crud.qna.start_session(current_user.id, params.query)
    crud.qna.store_user_qa(db, current_user.id, params.query, json.dumps(state), [])
    return {
        "status": True,
        "data": {
            "session_id": session_id,
            "state": state
        },
        "errormsg": None
    }


@router.post("/continue_chat/", response_model=schemas.QnaResponse)
async def continue_chat(*, db: Session = Depends(deps.get_db),params: schemas.ContinueChatRequest,
    current_user: User = Depends(deps.get_current_active_user)):
    # Redis se previous state fetch
    prev_state = crud.qna.get_session(current_user.id, params.session_id)
    if not prev_state:
        return {"status":False,"data":None,"errormsg":"Session expired or not found"}
    state = crud.qna.continue_session(
        user_id=current_user.id,
        session_id=params.session_id,
        query=params.query,
        user_input="",              # Agar user_input chahiye toh pass karo
        current_agent=prev_state.get("agent"),
        step=prev_state.get("step", 1)
    )

    # Update Redis aur DB
    crud.qna.store_user_qa(db, current_user.id, params.query, json.dumps(state), [])

    return { "status": True, "data": { "session_id": params.session_id, "state": state}, "errormsg": None}
