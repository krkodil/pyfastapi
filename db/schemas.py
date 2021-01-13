from typing import List, Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class TokenData(BaseModel):
    public_id: Optional[str] = None


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserApp(UserBase):
    public_id: str

    class Config:
        orm_mode = True


class User(UserBase):
    id: int
    public_id: str
    is_active: bool
    is_admin: bool
    items: List[Item] = []

    class Config:
        orm_mode = True
