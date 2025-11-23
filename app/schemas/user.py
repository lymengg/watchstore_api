from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    phone_number: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None


class User(BaseModel):
    username: str
    email: str
    phone_number: str

    model_config = {
        "from_attributes": True
    }
