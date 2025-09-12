import logging
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
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
from app.models.user import User, Customer, UserOTP
from app.models.status_base import UserRole, StatusEnum


_logger = logging.getLogger(__name__)


class CRUDLogin:

    def __init__(self):
        pass

    def check_valid_user(self, db: Session, email: EmailStr):
        return db.query(User).filter(User.username == email).first()
    

    # def forgot_password(self, db: Session, params):
    #     company_id = self.check_valid_company(db, params.email)
    #     if not company_id:
    #         return {'success': False, 'msg': 'Email Does Not Exist'}
    #     validity = datetime.utcnow() + timedelta(minutes=settings.OTP_VALIDITY_MINUTES)
    #     db.query(CompanyOTP).filter(CompanyOTP.email == params.email).delete()
    #     otp = generate_random_number(6)
    #     otp_id = CompanyOTP(**{'email': params.email, 'otp': otp, 'valid_until': validity})
    #     db.add(otp_id)
    #     db.commit()
    #     db.refresh(otp_id)
    #     sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    #     with open('mail-templates/forgot_password_mail.html') as f:
    #         html_text = f.read()
    #         html_text = html_text.replace('{CUSTOMER_NAME}', company_id.company_name).replace('{OTP}', otp_id.otp)
    #         html_content = HtmlContent(html_text)
    #         soup = BeautifulSoup(html_text, features="lxml")
    #         plain_text = soup.get_text()
    #         plain_text_content = Content("text/plain", plain_text)
    #     mail = Mail(Email(settings.SENDGRID_FROM_ACCOUNT), To(company_id.business_email),
    #                 "iera Reset Password - One Time Password", plain_text_content, html_content)
    #     sendgrid_client.send(message=mail)
    #     _logger.info("Login Forgot Password Mail Sent")
    #     return {'success': True, 'msg': 'OTP Generated and Sent Successfully'}

    def generate_otp(self, db: Session, params):
        validity = datetime.utcnow() + timedelta(minutes=settings.OTP_VALIDITY_MINUTES)
        db.query(UserOTP).filter(UserOTP.email == params.email).delete()
        otp = generate_random_number(6)
        otp_id = UserOTP(**{'email': params.email, 'otp': otp, 'valid_until': validity})
        db.add(otp_id)
        db.commit()
        db.refresh(otp_id)
        # sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        # with open('mail-templates/welcome_mail.html') as f:
        #     html_text = f.read()
        #     html_text = html_text.replace('{OTP}', otp_id.otp)
        #     html_content = HtmlContent(html_text)
        #     soup = BeautifulSoup(html_text, features="lxml")
        #     plain_text = soup.get_text()
        #     plain_text_content = Content("text/plain", plain_text)
        # mail = Mail(Email(settings.SENDGRID_FROM_ACCOUNT), To(params.email),
        #             "iera Verify Account - One Time Password", plain_text_content, html_content)
        # sendgrid_client.send(message=mail)
        _logger.info("Login Generate OTP Mail Sent")
        return {'success': True, 'msg': 'OTP Generated and Sent Successfully', 'data': {'otp': otp}}

    def authenticate(self, db: Session, params) -> dict:
        user_id = self.check_valid_user(db, params.email)
        if not user_id:
            return {'success': False, 'msg': 'Email Does Not Exist'}
        if not verify_password(params.password, user_id.password_hash):
            return {'success': False, 'msg': 'Invalid password'}
        return {
            'success': True,
            'msg': 'Logged in successfully',
            'data': {
                'access_token': security.create_access_token(
                    user_id.access_token,
                    expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                ),
                'username': user_id.username,
                'status': user_id.status.value, 
                'role': user_id.role.value, 
                'token_type': 'bearer'
            }
        }

    def register(self, db: Session, params) -> dict:
        user_id = self.check_valid_user(db, params.email)
        if user_id:
            return {'success': False, 'msg': 'Email Already Exist'}
        password_hash = get_password_hash(params.password)
        user_obj = User(username=params.email, password_hash=password_hash, 
                        role=UserRole.CUSTOMER, status=StatusEnum.ACTIVE)
        db.add(user_obj)
        db.commit()
        if user_obj:
            user_obj.access_token = f"{uuid4()}_{user_obj.id}"
            db.commit()
            customer_obj = Customer(user_id=user_obj.id, phone=params.phone, email=params.email,
                                    status=StatusEnum.ACTIVE)
            db.add(customer_obj)
            db.commit()
            otp = self.generate_otp(db, params)
        db.refresh(user_obj)
        return {'success': True, 'msg': 'User Registered Successfully', 'data': {'otp': otp.get('data').get('otp')}}


    def verify_otp(self, db: Session, params) -> dict:
        verify_id = db.query(User).filter(User.username == params.email).first()
        if not verify_id:
            return {'success': False, 'msg': 'Email Does Not Exist'}
        otp_obj = db.query(UserOTP).filter(UserOTP.email == params.email).first()
        if not otp_obj:
            return {'success': False, 'msg': 'Otp is not valid or not exist'}
        if params.otp != otp_obj.otp:
            return {'success': False, 'msg': 'Otp is not valid'}
        if datetime.utcnow() > otp_obj.valid_until:
            return {'success': False, 'msg': 'Otp Timeout, So it is not valid'}
        db.query(UserOTP).filter(UserOTP.email == params.email).delete()
        verify_id.verified = True
        db.commit()
        return {'success': True, "msg": "Email Verified in successfully"}

    # def verify_forgot_password_otp(self, db: Session, params) -> dict:
    #     company_id = self.check_valid_company(db, params.email)
    #     if not company_id:
    #         return {'success': False, 'msg': 'Email Does Not Exist'}
    #     otp_obj = db.query(CompanyOTP).filter(CompanyOTP.email == params.email).first()
    #     if not otp_obj:
    #         return {'success': False, 'msg': 'Otp is not valid or not exist'}
    #     if params.otp != otp_obj.otp:
    #         return {'success': False, 'msg': 'Otp is not valid'}
    #     if datetime.utcnow() > otp_obj.valid_until:
    #         return {'success': False, 'msg': 'Otp Timeout, So it is not valid'}
    #     db.query(CompanyOTP).filter(CompanyOTP.email == params.email).delete()
    #     db.commit()
    #     return {'success': True, "msg": "Email Verified in successfully", 'data': {
    #         'access_token': security.create_access_token(company_id.access_token, expires_delta=timedelta(
    #             minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)), 'token_type': 'bearer'}}

    # def verify_otp_email(self, db: Session, params):
    #     company_id = self.check_valid_company(db, params.email)
    #     if not company_id:
    #         return {'success': False, 'msg': 'Email Does Not Exist'}
    #     otp_obj = db.query(CompanyOTP).filter(CompanyOTP.email == params.email).first()
    #     if not otp_obj:
    #         return {'success': False, 'msg': 'Otp is not valid or not exist'}
    #     if params.otp != otp_obj.otp:
    #         return {'success': False, 'msg': 'Otp is not valid'}
    #     if datetime.utcnow() > otp_obj.valid_until:
    #         return {'success': False, 'msg': 'Otp Timeout, So it is not valid'}
    #     db.query(CompanyOTP).filter(CompanyOTP.email == params.email).delete()
    #     db.commit()
    #     return {'success': True, "msg": "Email Verified in successfully", 'data': {
    #         'access_token': security.create_access_token(company_id.access_token, expires_delta=timedelta(
    #             minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)),
    #         'token_type': 'bearer'
    #     }}

    # def reset_password(self, db: Session, current_company, params):
    #     if not verify_password(params.old_password, current_company.password_hash):
    #         return {'success': False, 'msg': 'Invalid current password'}
    #     new_password_hash = get_password_hash(params.new_password)
    #     current_company.password_hash = new_password_hash
    #     db.commit()
    #     db.refresh(current_company)
    #     return {'success': True, 'msg': 'Password Set Successfully'}

    # def set_password(self, db: Session, current_company, params):
    #     new_password_hash = get_password_hash(params.password)
    #     current_company.password_hash = new_password_hash
    #     db.commit()
    #     db.refresh(current_company)
    #     return {'success': True, 'msg': 'Password Changed Successfully'}


login = CRUDLogin()
