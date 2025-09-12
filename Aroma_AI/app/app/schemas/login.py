from typing import Optional

from pydantic import BaseModel, EmailStr


class Login(BaseModel):
    email: EmailStr
    password: str


class Register(BaseModel):
    phone: str
    email: EmailStr
    password: str


class VerifyOtp(BaseModel):
    email: EmailStr
    otp: str


class LoginOTP(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict]


# class ResetPassword(BaseModel):
#     old_password: str
#     new_password: str


# class SetPassword(BaseModel):
#     password: str
