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


@router.post("/", response_model=schemas.LoginResponse)
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



@router.post("/signup", response_model=schemas.LoginResponse)
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


@router.post("/verify-otp/", response_model=schemas.LoginResponse)
def get_otp_verified(*, db: Session = Depends(deps.get_db), params: schemas.VerifyOtp):
    try:
        _logger.info("Login Get Otp Verified: Params: %r" % params)
        response = crud.login.verify_otp(db, params)
        _logger.info("Login Get Otp Response: %r" % response)
        return JSONResponse(status_code=200 if response.get('success') else 400,
                            content={'success': response.get('success'), "message": response.get('msg')})
    except Exception as e:
        _logger.error("Exception in Login Get Otp: %s" % e)
        return JSONResponse(status_code=400, content={'success': False, "message": str(e)})


# @router.put("/reset-password/", response_model=schemas.LoginResponse)
# def reset_password(*, current_company: Companies = Depends(deps.get_current_active_company),
#                    db: Session = Depends(deps.get_db), params: schemas.ResetPassword) -> Any:
#     try:
#         _logger.info("Login Reset Password: Params: %r Company: %s" % (params, current_company.id))
#         response = crud.login.reset_password(db, current_company, params)
#         _logger.info("Login Reset Password Response: %r" % response)
#         return JSONResponse(status_code=200 if response.get('success') else 400,
#                             content={'success': response.get('success'), "message": response.get('msg')})
#     except Exception as e:
#         _logger.error("Exception in Login Reset Password: %s" % e)
#         return JSONResponse(status_code=400, content={'success': False, "message": str(e)})


# @router.post("/forgot-password/", response_model=schemas.LoginResponse)
# def forgot_password(*, db: Session = Depends(deps.get_db), params: schemas.LoginOTP) -> Any:
#     try:
#         _logger.info("Login Forgot Password: Params: %r" % params)
#         response = crud.login.forgot_password(db, params)
#         _logger.info("Login Forgot Password Response: %r" % response)
#         return JSONResponse(status_code=200 if response.get('success') else 400,
#                             content={'success': response.get('success'), "message": response.get('msg')})
#     except Exception as e:
#         _logger.error("Exception in Login Forgot Password: %s" % e)
#         return JSONResponse(status_code=400, content={'success': False, "message": str(e)})


# @router.post("/verify-otp-email/", response_model=schemas.LoginResponse)
# def verify_otp_email(*, db: Session = Depends(deps.get_db), params: schemas.VerifyOtp) -> Any:
#     try:
#         _logger.info("Login Verify Otp Email: Params: %r" % params)
#         response = crud.login.verify_otp_email(db, params)
#         _logger.info("Login Verify Otp Email Response: %r" % response)
#         return JSONResponse(status_code=200 if response.get('success') else 400,
#                             content={'success': response.get('success'), "message": response.get('msg'),
#                                      'data': response.get('data')})
#     except Exception as e:
#         _logger.error("Exception in Login Verify Otp Email: %s" % e)
#         return JSONResponse(status_code=400, content={'success': False, "message": str(e)})


# @router.post("/verify-otp-forgot-password/", response_model=schemas.LoginResponse)
# def verify_otp_forgot_password(*, db: Session = Depends(deps.get_db), params: schemas.VerifyOtp) -> Any:
#     try:
#         _logger.info("Login Verify Otp Forgot Password: Params: %r" % params)
#         response = crud.login.verify_forgot_password_otp(db, params)
#         _logger.info("Login Verify Otp Forgot Password Response: %r" % response)
#         return JSONResponse(status_code=200 if response.get('success') else 400,
#                             content={'success': response.get('success'), "message": response.get('msg'),
#                                      'data': response.get('data')})
#     except Exception as e:
#         _logger.error("Exception in Login Verify Otp Forgot Password: %s" % e)
#         return JSONResponse(status_code=400, content={'success': False, "message": str(e)})


# @router.post("/set-password/", response_model=schemas.LoginResponse)
# def set_password(*, current_company: Companies = Depends(deps.get_current_active_company),
#                  db: Session = Depends(deps.get_db), params: schemas.SetPassword) -> Any:
#     try:
#         _logger.info("Login Set Password: Params: %r Company: %s" % (params, current_company.id))
#         response = crud.login.set_password(db, current_company, params)
#         _logger.info("Login Set Password Response: %r" % response)
#         return JSONResponse(status_code=200 if response.get('success') else 400,
#                             content={'success': response.get('success'), "message": response.get('msg')})
#     except Exception as e:
#         _logger.error("Exception in Login Set Password: %s" % e)
#         return JSONResponse(status_code=400, content={'success': False, "message": str(e)})
