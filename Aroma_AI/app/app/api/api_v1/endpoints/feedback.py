import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.user import User
from app.api import deps

_logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/create", response_model=schemas.FeedbackResponse)
def create_feedback(
    *,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
    params: schemas.FeedbackCreate,
):
    try:
        response = crud.feedback.create(db=db, obj_in=params, current_user=current_user)
        return JSONResponse(status_code=200 if response.get("success") else 400, content=response)
    except Exception as e:
        _logger.error(f"Exception in Create Feedback: {e}")
        return JSONResponse(status_code=400, content={"success": False, "msg": str(e)})


@router.get("/get/{feedback_id}", response_model=schemas.FeedbackResponse)
def get_feedback(
    *,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
    feedback_id: int,
):
    try:
        response = crud.feedback.get(db=db, feedback_id=feedback_id)
        return JSONResponse(status_code=200 if response.get("success") else 400, content=response)
    except Exception as e:
        _logger.error(f"Exception in Get Feedback: {e}")
        return JSONResponse(status_code=400, content={"success": False, "msg": str(e)})


@router.get("/order/{order_id}", response_model=schemas.FeedbackResponse)
def get_feedback_by_order(
    *,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
    order_id: int,
):
    try:
        response = crud.feedback.get_by_order(db=db, order_id=order_id, current_user=current_user)
        return JSONResponse(status_code=200 if response.get("success") else 400, content=response)
    except Exception as e:
        _logger.error(f"Exception in Get Feedback By Order: {e}")
        return JSONResponse(status_code=400, content={"success": False, "msg": str(e)})


@router.get("/list", response_model=schemas.FeedbackListResponse)
def list_feedbacks(
    *,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    try:
        response = crud.feedback.get_multi(db=db, current_user=current_user)
        return JSONResponse(status_code=200 if response.get("success") else 400, content=response)
    except Exception as e:
        _logger.error(f"Exception in List Feedbacks: {e}")
        return JSONResponse(status_code=400, content={"success": False, "msg": str(e)})


@router.put("/update/{feedback_id}", response_model=schemas.FeedbackResponse)
def update_feedback(
    *,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
    feedback_id: int,
    params: schemas.FeedbackUpdate,
):
    try:
        response = crud.feedback.update(db=db, feedback_id=feedback_id, obj_in=params, current_user=current_user)
        return JSONResponse(status_code=200 if response.get("success") else 400, content=response)
    except Exception as e:
        _logger.error(f"Exception in Update Feedback: {e}")
        return JSONResponse(status_code=400, content={"success": False, "msg": str(e)})


@router.delete("/delete/{feedback_id}", response_model=schemas.FeedbackResponse)
def delete_feedback(
    *,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
    feedback_id: int,
):
    try:
        response = crud.feedback.remove(db=db, feedback_id=feedback_id, current_user=current_user)
        return JSONResponse(status_code=200 if response.get("success") else 400, content=response)
    except Exception as e:
        _logger.error(f"Exception in Delete Feedback: {e}")
        return JSONResponse(status_code=400, content={"success": False, "msg": str(e)})
