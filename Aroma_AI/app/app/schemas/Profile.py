from typing import List, Optional

from pydantic import BaseModel, EmailStr

class AddressUpdate(BaseModel):
    address_line: str
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    address_type: Optional[str] = "home"

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    addresses: Optional[List[AddressUpdate]] = None

class ProfileResponse(BaseModel):
    success: bool
    message: str
    data: dict | None = None