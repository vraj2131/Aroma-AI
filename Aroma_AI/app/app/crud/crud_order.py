import logging
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.order import Order, OrderItem, MenuItem
from app.models.user import Customer, User
from app.models.table import Table
from app.models.status_base import StatusEnum
from collections import defaultdict

_logger = logging.getLogger(__name__)


class CRUDOrder:

    def book_order(self, db: Session, user: User, params) -> dict:
        customer = db.query(Customer).filter(Customer.user_id == user.id).first()
        if not customer:
            return {'success': False, 'msg': 'Customer profile not found'}
        try:
            today = datetime.utcnow().date()
            if params.order_type == "delivery":
                new_order = Order(
                    user_id=user.id,
                    table_id=None,
                    order_type="delivery",
                    status="pending",
                    payment_status="unpaid",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(new_order)
                db.flush()
                for item in params.items:
                    menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
                    if not menu_item:
                        return {"success": False, "msg": f"Menu item {item.menu_item_id} not found"}
                    new_order_item = OrderItem(
                        order_id=new_order.id,
                        item_type=menu_item.item_type,
                        item_name=menu_item.item_name,
                        customization=item.customization,
                        quantity=item.quantity,
                        price=menu_item.price * item.quantity
                    )
                    db.add(new_order_item)
                db.commit()
                db.refresh(new_order)
                return {
                    "success": True,
                    "msg": "Delivery order placed successfully",
                    "data": {"order_id": new_order.id}
                }
            existing_order = (
                db.query(Order)
                .filter(
                    Order.user_id == user.id,
                    Order.table_id == params.table_id,
                    func.date(Order.created_at) == today,
                    Order.status.in_(["pending", "confirmed", "preparing", "completed"]),
                    Order.order_type != "delivery",
                    Order.payment_status != "paid"
                )
                .first()
            )
            if existing_order and params.order_type in ["take_away", "dine_in"]:
                for item in params.items:
                    menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
                    if not menu_item:
                        return {"success": False, "msg": f"Menu item {item.menu_item_id} not found"}
                    new_order_item = OrderItem(
                        order_id=existing_order.id,
                        item_type=menu_item.item_type,
                        item_name=menu_item.item_name,
                        customization=item.customization,
                        quantity=item.quantity,
                        price=menu_item.price * item.quantity
                    )
                    db.add(new_order_item)
                existing_order.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(existing_order)
                return {
                    "success": True,
                    "msg": "Items added to existing unpaid order",
                    "data": {"order_id": existing_order.id}
                }
            table = db.query(Table).filter(Table.id == params.table_id, Table.User_id == user.id).first()
            if not table and params.order_type == "dine_in":
                return {'success': False, 'msg': 'Table not found'}
            new_order = Order(
                user_id=user.id,
                table_id=table.id if table else None,
                order_type=params.order_type,
                status="pending",
                payment_status="unpaid",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_order)
            db.flush()
            for item in params.items:
                menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
                if not menu_item:
                    return {"success": False, "msg": f"Menu item {item.menu_item_id} not found"}
                new_order_item = OrderItem(
                    order_id=new_order.id,
                    item_type=menu_item.item_type,
                    item_name=menu_item.item_name,
                    customization=item.customization,
                    quantity=item.quantity,
                    price=menu_item.price * item.quantity
                )
                db.add(new_order_item)
            db.commit()
            db.refresh(new_order)
            return {
                "success": True,
                "msg": "New order booked successfully",
                "data": {"order_id": new_order.id}
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "msg": str(e)}


    def update_order_status(self, db: Session, user: User, params) -> dict:
        try:
            customer = db.query(Customer).filter(Customer.user_id == user.id).first()
            if not customer:
                return {"success": False, "msg": "Customer profile not found"}
            if user.role == "customer":
                order = db.query(Order).filter(Order.id == params.order_id, Order.user_id == user.id).first()
            else:
                order = db.query(Order).filter(Order.id == params.order_id).first()
            if not order:
                return {"success": False, "msg": "Order not found"}
            if order.status == "cancelled":
                return {"success": True, "msg": "Sorry Order be cancelled"}
            if params.status == "cancelled":
                if order.status in ["preparing", "completed"]:
                    return {"success": False, "msg": f"Order cannot be cancelled once it's {order.status}"}
            allowed_statuses = ["pending", "confirmed", "preparing", "completed", "cancelled"]
            if params.status and params.status in allowed_statuses:
                # return {"success": False, "msg": "Invalid status value"}
                if params.status:
                    order.status = params.status
                    db.commit()

            if params.payment_status:
                order.payment_status = params.payment_status
                db.commit()
            order.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(order)
            return {
                "success": True,
                "msg": "Order status updated successfully",
                "data": {
                    "order_id": order.id,
                    "status": order.status,
                    "payment_status": order.payment_status
                }
            }

        except Exception as e:
            db.rollback()
            return {"success": False, "msg": str(e)}

        
    def fetch_orders(self, db: Session, user: User, params) -> dict:
        try:
            page = getattr(params, "page", 1) or 1
            limit = getattr(params, "limit", 10) or 10

            query = (
                db.query(Order)
                .options(
                    joinedload(Order.items),  
                    joinedload(Order.delivery)
                )
            )
            if user.role == "customer":
                query = query.filter(Order.user_id == user.id)
            if getattr(params, "order_id", None):
                query = query.filter(Order.id == params.order_id)
            if getattr(params, "order_status", None):
                query = query.filter(Order.status == params.order_status)
            if getattr(params, "order_type", None):
                query = query.filter(Order.order_type == params.order_type)
            if getattr(params, "from_date", None):
                query = query.filter(func.date(Order.created_at) >= params.from_date.date())
            if getattr(params, "to_date", None):
                query = query.filter(func.date(Order.created_at) <= params.to_date.date())

            total_records = query.count()
            total_pages = (total_records + limit - 1) // limit

            orders = (
                query.order_by(Order.created_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
                .all()
            )

            order_list = []
            for order in orders:
                items = [
                    {
                        "item_id": item.id,
                        "item_type": item.item_type,
                        "item_name": item.item_name,
                        "customization": item.customization,
                        "quantity": item.quantity,
                        "price": item.price
                    }
                    for item in order.items
                ]

                delivery_data = None
                if order.delivery:
                    delivery_data = {
                        "delivery_id": order.delivery.id,
                        "delivery_partner": order.delivery.user_id,
                        "delivery_address": order.delivery.address_id,
                        "delivery_status": order.delivery.delivery_status,
                        "expected_time": order.delivery.expected_time.isoformat() if order.delivery.expected_time else None,
                        "actual_time": order.delivery.actual_time.isoformat() if order.delivery.actual_time else None,
                    }

                order_list.append({
                    "order_id": order.id,
                    "order_type": order.order_type,
                    "status": order.status,
                    "payment_status": order.payment_status,
                    "table_id": order.table_id,
                    "created_at": order.created_at.isoformat() if order.created_at else None,
                    "updated_at": order.updated_at.isoformat() if order.updated_at else None,
                    "items": items,
                    "delivery": delivery_data
                })
            return {
                "success": True,
                "msg": "Orders fetched successfully",
                "data": {
                    "orders": order_list,
                    "total_records": total_records,
                    "total_pages": total_pages,
                    "current_page": page,
                    "per_page": limit
                }
            }

        except Exception as e:
            return {"success": False, "msg": str(e)}


        
    def get_menu_items(self, db: Session, user: User, params):
        customer = db.query(Customer).filter(Customer.user_id == user.id).first()
        if not customer:
            return {"success": False, "msg": "Customer profile not found", "data": []}
        try:
            query = db.query(MenuItem)
            if user.role == "customer":
                query = query.filter(MenuItem.is_available == True)
            if params.item_type:
                query = query.filter(MenuItem.item_type == params.item_type)
            if params.item_name:
                query = query.filter(MenuItem.item_name.ilike(f"%{params.item_name}%"))

            items = query.all()
            grouped_items = defaultdict(list)
            for item in items:
                grouped_items[item.item_type].append({
                    "id": item.id,
                    "item_name": item.item_name,
                    "description": item.description,
                    "price": item.price,
                    "is_available": item.is_available,
                })
            fixed_order = ["starter", "main_course", "beverage", "dessert"]
            ordered_items = []
            for t in fixed_order:
                if t in grouped_items:
                    ordered_items.append({"item_type": t, "items": grouped_items[t]})

            return {
                "success": True,
                "msg": "Menu items fetched successfully",
                "data": ordered_items,
            }
        except Exception as e:
            return {"success": False, "msg": str(e), "data": []}
        
    def update_menu_item(self, db: Session, user: User, params) -> dict:
        try:
            if user.role == "customer":
                return {"success": False, "msg": "No Access"}
            item = db.query(MenuItem).filter(MenuItem.id == params.id).first()
            if not item:
                return {"success": False, "msg": "Menu item not found", "data": {}}

            if params.price is not None:
                item.price = params.price
            if params.is_available is not None:
                item.is_available = params.is_available
            db.commit()
            db.refresh(item)
            data = {
                "id": item.id,
                "item_type": item.item_type,
                "item_name": item.item_name,
                "description": item.description,
                "price": item.price,
                "is_available": item.is_available,
            }

            return {"success": True, "msg": "Menu item updated successfully", "data": data}
        except Exception as e:
            return {"success": False, "msg": str(e), "data": {}}


order = CRUDOrder()
