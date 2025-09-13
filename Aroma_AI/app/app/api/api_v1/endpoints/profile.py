from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app import crud
from app import schemas
from app.api import deps
from app.core import security
from app.models.user import User
from app.api import deps
import logging

_logger = logging.getLogger(__name__)
router = APIRouter()

@router.put("/update-profile/", response_model=schemas.ProfileResponse)
def update_profile(*, current_user: User = Depends(deps.get_current_active_user),
                   db: Session = Depends(deps.get_db), params: schemas.ProfileUpdate):
    try:
        _logger.info("Update Profile: Params: %r" % params)
        response = crud.profile.update_profile(db, current_user, params)
        _logger.info("Update Profile Response: %r" % response)
        return JSONResponse(
            status_code=200 if response.get('success') else 400,
            content={
                'success': response.get('success'),
                "message": response.get('msg'),
                'data': response.get('data')
            }
        )
    except Exception as e:
        _logger.error("Exception in Update Profile: %s" % e)
        return JSONResponse(
            status_code=400,
            content={'success': False, "message": str(e)}
        )
@router.get("/fetch-profile/", response_model=schemas.ProfileResponse)
def fetch_profile(*, current_user: User = Depends(deps.get_current_active_user),
                  db: Session = Depends(deps.get_db)):
    try:
        _logger.info(f"Fetch Profile for user_id: {current_user.id}")
        response = crud.profile.fetch_profile(db, current_user)
        _logger.info(f"Fetch Profile Response: {response}")
        return JSONResponse(
            status_code=200 if response.get("success") else 400,
            content={
                "success": response.get("success"),
                "message": response.get("msg"),
                "data": response.get("data")
            }
        )
    except Exception as e:
        _logger.error(f"Exception in Fetch Profile: {e}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": str(e)}
        )
