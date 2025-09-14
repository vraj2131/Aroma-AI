import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.user import User
from app.api import deps

_logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/update-status/", response_model=schemas.DeliveryResponse)
def update_delivery_status(*, current_user: User = Depends(deps.get_current_active_user),
               db: Session = Depends(deps.get_db), params: schemas.DeliveryStatus):
    try:
        response = crud.delivery.update_delivery_status(db, current_user, params)
        return JSONResponse(
            status_code=200 if response.get("success") else 400,
            content={
                "success": response.get("success"),
                "message": response.get("msg"),
                "data": response.get("data")
            }
        )
    except Exception as e:
        _logger.error(f"Exception in update status: {e}")
        return JSONResponse(status_code=400, content={"success": False, "message": str(e)})
    
@router.post("/get_deliveries/", response_model=schemas.DeliveryResponse)
def get_deliveries(*, current_user: User = Depends(deps.get_current_active_user),
               db: Session = Depends(deps.get_db), params: schemas.DeliveryDetails):
    try:
        response = crud.delivery.get_delivery_details(db, current_user, params)
        return JSONResponse(
            status_code=200 if response.get("success") else 400,
            content={
                "success": response.get("success"),
                "message": response.get("msg"),
                "data": response.get("data")
            }
        )
    except Exception as e:
        _logger.error(f"Exception in get delivery details: {e}")
        return JSONResponse(status_code=400, content={"success": False, "message": str(e)})
