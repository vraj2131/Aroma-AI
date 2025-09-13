import logging
from datetime import datetime, timedelta

from pydantic import EmailStr
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core import security
from app.core.common import generate_random_number
from app.core.config import settings
from app.core.security import get_password_hash
from app.core.security import verify_password
from app.models.user import User, Customer
from app.models.address import Address
from app.models.status_base import UserRole, StatusEnum


_logger = logging.getLogger(__name__)


class CRUDProfile:

    def update_profile(self, db: Session, user: User, params) -> dict:
        try:
            customer = db.query(Customer).filter(Customer.user_id == user.id).first()
            if not customer:
                return {'success': False, 'msg': 'Customer profile not found'}
            if params.full_name:
                customer.full_name = params.full_name
            if params.phone:
                customer.phone = params.phone
            if params.email:
                customer.email = params.email
            if params.addresses:
                db.query(Address).filter(Address.customer_id == customer.id).delete()
                for addr in params.addresses:
                    new_addr = Address(
                        customer_id=customer.id,
                        address_line=addr.address_line,
                        city=addr.city,
                        state=addr.state,
                        postal_code=addr.postal_code,
                        address_type=addr.address_type or "home"
                    )
                    db.add(new_addr)

            db.commit()
            db.refresh(customer)

            return {
                'success': True,
                'msg': 'Profile updated successfully',
                'data': {}
            }
        except Exception as e:
            return {'success': False, 'msg': str(e)}

    def fetch_profile(self, db: Session, user: User) -> dict:
        try:
            customer = db.query(Customer).filter(Customer.user_id == user.id).first()
            if not customer:
                return {"success": False, "msg": "Customer profile not found", "data": {}}

            addresses = db.query(Address).filter(Address.customer_id == customer.id).all()
            address_list = [
                {
                    "address_line": addr.address_line,
                    "city": addr.city,
                    "state": addr.state,
                    "postal_code": addr.postal_code,
                    "address_type": addr.address_type
                }
                for addr in addresses
            ]

            data = {
                "full_name": customer.full_name,
                "phone": customer.phone,
                "email": customer.email,
                "addresses": address_list
            }

            return {"success": True, "msg": "Profile fetched successfully", "data": data}
        except Exception as e:
            return {"success": False, "msg": str(e), "data": {}}


profile = CRUDProfile()