import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.user import User
from app.api import deps

_logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/book/", response_model=schemas.OrderResponse)
def book_table(*, current_user: User = Depends(deps.get_current_active_user),
               db: Session = Depends(deps.get_db), params: schemas.OrderCreate):
    try:
        response = crud.table.book_table(db, current_user, params)
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