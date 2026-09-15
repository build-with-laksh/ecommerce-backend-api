from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserPublic(BaseModel):
    id: int
    username: str

class UserPrivate(UserPublic):
    email: EmailStr

