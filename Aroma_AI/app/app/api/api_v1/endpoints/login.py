import logging
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud
from app import schemas
from app.api import deps

_logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/verify-otp/", response_model=schemas.LoginResponse)
def login(*, db: Session = Depends(deps.get_db), params: schemas.Login) -> Any:
    try:
        _logger.info("Login: Params: %r" % params)
        response = crud.login.authenticate(db, params)
        _logger.info("Login Response: %r" % response)
        return JSONResponse(status_code=200 if response.get('success') else 400,
                            content={'success': response.get('success'), "message": response.get('msg'),
                                     'data': response.get('data')})
    except Exception as e:
        _logger.error("Exception in Login: %s" % e)
        return JSONResponse(status_code=400, content={'success': False, "message": str(e)})
    

@router.post("/", response_model=schemas.LoginResponse)
def register(*, db: Session = Depends(deps.get_db), params: schemas.Register) -> Any:
    try:
        _logger.info("Register: Params: %r" % params)
        response = crud.login.register(db, params)
        _logger.info("Register Response: %r" % response)
        return JSONResponse(status_code=200 if response.get('success') else 400,
                            content={'success': response.get('success'), "message": response.get('msg'),
                                     'data': response.get('data')})
    except Exception as e:
        _logger.error("Exception in Register: %s" % e)
        return JSONResponse(status_code=400, content={'success': False, "message": str(e)})

@router.post("/get-otp/", response_model=schemas.LoginResponse)
def get_otp_email(*, db: Session = Depends(deps.get_db), params: schemas.LoginOTP) -> Any:
    try:
        _logger.info("Login Get Otp: Params: %r" % params)
        response = crud.login.generate_otp(db, params)
        _logger.info("Login Get Otp Response: %r" % response)
        return JSONResponse(status_code=200 if response.get('success') else 400,
                            content={'success': response.get('success'), "message": response.get('msg'),
                                     'data': response.get('data')})
    except Exception as e:
        _logger.error("Exception in Login Get Otp: %s" % e)
        return JSONResponse(status_code=400, content={'success': False, "message": str(e)})
