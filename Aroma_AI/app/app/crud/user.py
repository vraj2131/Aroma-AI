import logging
from typing import Optional
from uuid import uuid4

import requests
from fastapi.encoders import jsonable_encoder
from redis import StrictRedis
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.core.config import settings

from app.core.security import get_password_hash

from app.models.user import User

_logger = logging.getLogger(__name__)


class CRUDUser:

    def __init__(self):
        pass

    def is_active(self, company_obj: User) -> bool:
        return company_obj.verified

    def check_valid_user(self, db: Session, access_token: str) -> Optional[User]:
        return db.query(User).filter(User.access_token == access_token).first()

    def check_company_email(self, db: Session, params) -> dict:
        company_id = db.query(User).filter(User.username == params.business_email).first()
        if company_id:
            return {'success': False, 'msg': 'Company Email already Exists'}
        return {'success': True, 'msg': 'Company Email not Exists'}
    
    def check_is_admin(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email, User.role == 'manager').first()
user = CRUDUser()