from datetime import date, timedelta
import logging
import os
from app.models.user import User
from app.models import Delivery, Order, Customer, Address

_logger = logging.getLogger(__name__)


class DeliveryCRUD:
    """
    Handles document-related operations including upload, deletion,
    and checking the vectorstore processing status via Celery tasks.
    """

    def __init__(self):
        pass
    
    def update_delivery_status(self, db,current_user, params):
        try:
            # order = db.query(Order).filter(Order.id == params.order_id).first()
            delivery=db.query(Delivery).filter(Delivery.order_id == params.order_id).first()
            if not delivery:
                return {"success": False, "msg": "Delivery not found"}
            if params.status == "completed":
                delivery.delivery_status = "completed"
                order = db.query(Order).filter(Order.id == params.order_id).first()
                order.payment_status = "paid"
            if delivery.delivery_status == "waiting":
                now= date.utcnow()
                user = db.query(User).filter(
                        User.role == 'delivery',
                        User.delivery_status == 'available').first()
                delivery.delivery_status="assigned"
                delivery.user_id=user.id
                delivery.expected_time= now + timedelta(minutes=20) # assuming 20 mins for delivery
                delivery.actual_time= now + timedelta(minutes=20)
            db.commit()
            db.refresh(delivery)    
            return {
                "success": True,
                "msg": "Delivery status updated successfully",
                "data":{} }
        except Exception as e:
            _logger.error(f"Error in update_delivery_status: {str(e)}")
            return {"success": False, "msg": "Error updating delivery status"}
        
    def get_delivery_details(self, db, current_user,params):
        try:
            delivery = db.query(Delivery)
            if current_user.role == 'customer':
                delivery = delivery.filter(Delivery.order_id == params.order_id)
            deliveries = delivery.all()
            final_data = []
            for delivery in deliveries:
                    user = db.query(User).filter(User.id == delivery.user_id).first()
                    address = db.query(Address).filter(Address.id == delivery.address_id).first()
                    data={
                    "delivery_data" : {
                        "id": delivery.id,
                        "order_id": delivery.order_id,
                        "user_id": delivery.user_id,
                        "user_name": user.username if user else None,
                        "address_id": delivery.address_id,
                        "delivery_status": delivery.delivery_status,
                        "expected_time": delivery.expected_time,
                        "actual_time": delivery.actual_time
                    },
                    "address_data" : {
                        "city": address.city if address else None,
                        "state": address.state if address else None, 
                        "postal_code": address.postal_code if address else None, 
                        "address_line": address.address_line if address else None,
                        "address_type": address.address_type if address else None
                    }
                    }
                    final_data.append(data)

            return {
                        "success": True,
                        "msg": "Delivery details fetched successfully",
                        "data": final_data
                    }
              
        except Exception as e:
            _logger.error(f"Error in get_delivery_details: {str(e)}")
            return {"success": False, "msg": "Error fetching delivery details"}                                

delivery = DeliveryCRUD()