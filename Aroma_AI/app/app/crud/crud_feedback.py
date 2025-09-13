from sqlalchemy.orm import Session
from datetime import datetime
from app.models.feedback import Feedback
from app.models.order import Order
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate


def serialize_feedback(obj: Feedback):
    return {
        "id": obj.id,
        "order_id": obj.order_id,
        "rating": obj.rating,
        "comments": obj.comments,
        "created_at": obj.created_at.strftime("%Y-%m-%d %H:%M:%S") if obj.created_at else None
    }


class CRUDFeeedback:
    def create(self, db: Session, obj_in: FeedbackCreate, current_user):
        try:
            # Order check
            order = db.query(Order).filter(Order.id == obj_in.order_id).first()
            if not order:
                return {"success": False, "msg": "Order not found", "data": None}
            
            # Ensure only order owner can give feedback
            if order.user_id != current_user.id:
                return {"success": False, "msg": "Not authorized to give feedback on this order", "data": None}

            # Ensure only one feedback per order
            existing = db.query(Feedback).filter(Feedback.order_id == obj_in.order_id).first()
            if existing:
                return {"success": False, "msg": "Feedback already exists for this order", "data": serialize_feedback(existing)}

            db_obj = Feedback(
                order_id=obj_in.order_id,
                rating=obj_in.rating,
                comments=obj_in.comments,
                created_at=datetime.utcnow()
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return {"success": True, "msg": "Feedback created successfully", "data": serialize_feedback(db_obj)}
        except Exception as e:
            db.rollback()
            return {"success": False, "msg": str(e), "data": None}

    def update(self, db: Session, feedback_id: int, obj_in: FeedbackUpdate, current_user):
        db_obj = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not db_obj:
            return {"success": False, "msg": "Feedback not found", "data": None}
        
        # Ensure only owner of the feedback/order can update
        if db_obj.order.user_id != current_user.id:
            return {"success": False, "msg": "Not authorized to update this feedback", "data": None}

        if obj_in.rating is not None:
            db_obj.rating = obj_in.rating
        if obj_in.comments is not None:
            db_obj.comments = obj_in.comments
        db.commit()
        db.refresh(db_obj)
        return {"success": True, "msg": "Feedback updated successfully", "data": serialize_feedback(db_obj)}

    def get(self, db: Session, feedback_id: int):
        obj = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not obj:
            return {"success": False, "msg": "Feedback not found", "data": None}
        return {"success": True, "msg": "Feedback fetched successfully", "data": serialize_feedback(obj)}

    def get_by_order(self, db: Session, order_id: int, current_user):
        obj = db.query(Feedback).filter(Feedback.order_id == order_id).first()
        if not obj:
            return {"success": False, "msg": "Feedback for order not found", "data": None}
        
        # Ensure only owner can see his order feedback
        if obj.order.user_id != current_user.id:
            return {"success": False, "msg": "Not authorized to view this feedback", "data": None}
        
        return {"success": True, "msg": "Feedback fetched successfully", "data": serialize_feedback(obj)}

    def get_multi(self, db: Session, current_user):
        # If admin -> show all, else only user’s feedback
        if current_user.role == "admin":
            objs = db.query(Feedback).all()
        else:
            objs = db.query(Feedback).join(Order).filter(Order.user_id == current_user.id).all()
        
        if not objs:
            return {"success": False, "msg": "No feedbacks found", "data": []}
        
        feedback_list = [serialize_feedback(obj) for obj in objs]
        return {"success": True, "msg": "Feedbacks fetched successfully", "data": feedback_list}

    def remove(self, db: Session, feedback_id: int, current_user):
        db_obj = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not db_obj:
            return {"success": False, "msg": "Feedback not found", "data": None}
        
        # Only owner or admin can delete
        if db_obj.order.user_id != current_user.id and current_user.role != "admin":
            return {"success": False, "msg": "Not authorized to delete this feedback", "data": None}

        serialized = serialize_feedback(db_obj)
        db.delete(db_obj)
        db.commit()
        return {"success": True, "msg": "Feedback deleted successfully", "data": serialized}

feedback = CRUDFeeedback()
