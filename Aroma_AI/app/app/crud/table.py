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

    def book_tables(self, db: Session, user: User, params):
        customer = db.query(Customer).filter(Customer.user_id == user.id).first()
        if not customer:
            return {'success': False, 'msg': 'Customer profile not found'}
        booking_time = params.booking_date_time or datetime.now()
        results = []
        
        for table_id in params.table_ids:
            table = db.query(Table).filter(Table.id == table_id).first()
            if not table:
                results.append({"table_id": table_id, "success": False, "msg": "Table not found"})
                continue
            if table.status == "available":
                table.status = "occupied"
                table.User_id = user.id
                table.book_date_time = booking_time
                db.commit()
                db.refresh(table)
                results.append({"table_id": table.id, "success": True, "msg": "Table booked"})
            else:
                return {"success": True, "msg": "Table Already booked"}
        return {"success": True, "msg": "Table booked", "data": results}

    def table_cancel(self, db: Session, user: User, params):
        customer = db.query(Customer).filter(Customer.user_id == user.id).first()
        if not customer:
            return {'success': False, 'msg': 'Customer profile not found'}
        table = db.query(Table).filter(Table.id == params.table_id, Table.User_id == user.id).first()
        if not table:
            return {"success": False, "msg": "Table not found"}
        active_order = db.query(Order).filter(Order.table_id == params.table_id, Order.status in ["pending", "confirmed", "preparing"]).first()
        if active_order:
            return {"success": False, "msg": "Cannot cancel table, active order exists"}
        table.status = "available"
        table.User_id = None
        table.book_date_time = None
        db.commit()
        return {"success": True, "msg": "Table canceled", "table_id": table.id}
    
    def fetch_tables(self, db: Session, user: User):
        customer = db.query(Customer).filter(Customer.user_id == user.id).first()
        if not customer:
            return {'success': False, 'msg': 'Customer profile not found'}
        query = db.query(Table)
        if user.role == "customer":
            query = query.filter(Table.User_id == user.id )
        tables = query.all()
        if not tables:
            return {"success": False, "msg": "No tables found"}
        results = []
        for table in tables:
            active_order = None
            active_order = db.query(Order).filter(
                Order.table_id == table.id,
                Order.status.in_(["pending", "confirmed", "preparing"])
            ).first()
            results.append({
                "table_id": table.id,
                "number": table.number,
                "seats": table.seats,
                "status": table.status,
                "book_date_time": table.book_date_time.isoformat() if table.book_date_time else None,
                "has_active_order": bool(active_order) if active_order else False
            })
        
        return {"success": True, "msg": "fetch all table", "data": results}
    
    def update_tables_status(self, db: Session, user: User, params):
        customer = db.query(Customer).filter(Customer.user_id == user.id).first()
        if not customer:
            return {'success': False, 'msg': 'Customer profile not found'}
        if user.role == "customer":
            return {'success': False, 'msg': 'Access not provide'}
        table = db.query(Table).filter(Table.id == params.table_id).first()
        if not table:
            return {'success': False, 'msg': 'Table not found'}
        table.status = params.status
        table.book_date_time = None 
        table.User_id = None 
        db.commit()
        db.refresh(table)
        return {
            "success": True,
            "msg": f"Table {table.id} updated successfully"}



table = CRUDTable()