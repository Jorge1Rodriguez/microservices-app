from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool = True
    created_at: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: str

class LoginRequest(BaseModel):
    username: str
    password: str
