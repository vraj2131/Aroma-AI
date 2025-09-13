import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.user import User
from app.api import deps

_logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/book-order/", response_model=schemas.OrderResponse)
def book_order(*, current_user: User = Depends(deps.get_current_active_user),
               db: Session = Depends(deps.get_db), params: schemas.OrderCreate):
    try:
        response = crud.order.book_order(db, current_user, params)
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


@router.put("/update_order_status/", response_model=schemas.OrderResponse)
def update_order_status(*, current_user: User = Depends(deps.get_current_active_user),
               db: Session = Depends(deps.get_db), params: schemas.OrderStatus):
    try:
        response = crud.order.update_order_status(db, current_user, params)
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


@router.post("/fetch_orders/", response_model=schemas.OrderResponse)
def fetch_orders(*, current_user: User = Depends(deps.get_current_active_user),
               db: Session = Depends(deps.get_db), params: schemas.GetOrders):
    try:
        response = crud.order.fetch_orders(db, current_user, params)
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


@router.post("/menu-items/", response_model=schemas.OrderResponse)
def get_menu_items(*, current_user: User = Depends(deps.get_current_active_user),
               db: Session = Depends(deps.get_db), params: schemas.Menusearch):
    try:
        response = crud.order.get_menu_items(db, current_user, params)
        return JSONResponse(
            status_code=200 if response.get("success") else 400,
            content={
                "success": response.get("success"),
                "message": response.get("msg"),
                "data": response.get("data", []),
            },
        )
    except Exception as e:
        _logger.error("Exception in get_menu_items: %s", e)
        return JSONResponse(status_code=400, content={"success": False, "message": str(e)})
    
@router.put("/update-menu-item/", response_model=schemas.OrderResponse)
def update_menu_item(
    *, 
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
    params: schemas.MenuItemUpdate
):
    try:
        _logger.info(f"Update MenuItem: Params: {params}")
        response = crud.order.update_menu_item(db, current_user, params)
        _logger.info(f"Update MenuItem Response: {response}")
        return JSONResponse(
            status_code=200 if response.get("success") else 400,
            content={
                "success": response.get("success"),
                "message": response.get("msg"),
                "data": response.get("data"),
            }
        )
    except Exception as e:
        _logger.error(f"Exception in Update MenuItem: {e}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": str(e)},
        )
