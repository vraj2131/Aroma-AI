import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.user import User
from app.api import deps

_logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/book/", response_model=schemas.TableResponse)
def book_table(*, current_user: User = Depends(deps.get_current_active_user),
               db: Session = Depends(deps.get_db), params: schemas.TableBooking):
    try:
        response = crud.table.book_tables(db, current_user, params)
        return JSONResponse(
            status_code=200 if response.get("success") else 400,
            content={
                "success": response.get("success"),
                "message": response.get("msg"),
                "data": response.get("data")
            }
        )
    except Exception as e:
        _logger.error(f"Exception in Book Order: {e}")
        return JSONResponse(status_code=400, content={"success": False, "message": str(e)})
    
@router.put("/table-cancel/", response_model=schemas.OrderResponse)
def table_cancel(*, current_user: User = Depends(deps.get_current_active_user),
               db: Session = Depends(deps.get_db), params: schemas.TableCancel):
    try:
        response = crud.table.table_cancel(db, current_user, params)
        return JSONResponse(
            status_code=200 if response.get("success") else 400,
            content={
                "success": response.get("success"),
                "message": response.get("msg"),
                "data": response.get("data")
            }
        )
    except Exception as e:
        _logger.error(f"Exception in Cancel Order: {e}")
        return JSONResponse(status_code=400, content={"success": False, "message": str(e)})
    
@router.get("/", response_model=schemas.OrderResponse)
def fetch_tables(*, current_user: User = Depends(deps.get_current_active_user),
               db: Session = Depends(deps.get_db)):
    try:
        response = crud.table.fetch_tables(db, current_user)
        return JSONResponse(
            status_code=200 if response.get("success") else 400,
            content={
                "success": response.get("success"),
                "message": response.get("msg"),
                "data": response.get("data")
            }
        )
    except Exception as e:
        _logger.error(f"Exception in Cancel Order: {e}")
        return JSONResponse(status_code=400, content={"success": False, "message": str(e)})
    
@router.put("/update/", response_model=schemas.OrderResponse)
def update_tables_status(*, current_user: User = Depends(deps.get_current_active_user),
               db: Session = Depends(deps.get_db), params: schemas.TableCancel):
    try:
        response = crud.table.update_tables_status(db, current_user, params)
        return JSONResponse(
            status_code=200 if response.get("success") else 400,
            content={
                "success": response.get("success"),
                "message": response.get("msg"),
                "data": response.get("data")
            }
        )
    except Exception as e:
        _logger.error(f"Exception in Cancel Order: {e}")
        return JSONResponse(status_code=400, content={"success": False, "message": str(e)})