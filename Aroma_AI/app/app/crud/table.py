import logging
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.order import Order
from app.models.user import Customer, User
from app.models.table import Table
from app.models.waitingList import WaitingList
from app.models.status_base import StatusEnum
from collections import defaultdict
from datetime import date

_logger = logging.getLogger(__name__)

class CRUDTable:
    def book_table(self, db: Session, user: User, params):
        customer = db.query(Customer).filter(Customer.user_id == user.id).first()
        if not customer:
            return {'success': False, 'msg': 'Customer profile not found'}
        table = db.query(Table).filter(Table.id == params.table_id).first()
        if not table:
            return {"success": False, "message": "Table not found"}
        if table.status != "available":
            max_pos = db.query(WaitingList).filter(WaitingList.booking_date == date.today()).count()
            waiting = WaitingList(user_id=user.id, position=max_pos + 1)
            db.add(waiting)
            db.commit()
            return {"success": True, "message": "Table full, added to waiting list"}
        table.status = "occupied"
        table.User_id = user.id
        table.book_date_time = params.booking_time
        db.commit()
        db.refresh(table)
        return {"success": True, "message": "Table booked", "table_id": table.id}

    def cancel_table(self, db: Session, user: User, params):
        customer = db.query(Customer).filter(Customer.user_id == user.id).first()
        if not customer:
            return {'success': False, 'msg': 'Customer profile not found'}
        table = db.query(Table).filter(Table.id == params.table_id).first()
        if not table:
            return {"success": False, "message": "Table not found"}
        active_order = db.query(Order).filter(Order.table_id == params.table_id, Order.status != "cancelled").first()
        if active_order:
            return {"success": False, "message": "Cannot cancel table, active order exists"}
        table.status = "available"
        table.User_id = None
        table.book_date_time = None
        db.commit()
        return {"success": True, "message": "Table canceled", "table_id": table.id}

table = CRUDTable()