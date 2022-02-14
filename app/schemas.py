from typing import Optional
from pydantic import BaseModel, EmailStr, conint
from datetime import datetime

# Base Model used by the posts
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

# Model for creating users
class CreateUser(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True

# Model to generate new posts and update existing posts
class CreatePost(PostBase):
    pass

# Model for the response from the api
class PostOut(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True


class PostCount(BaseModel):
    Post: PostOut
    Votes: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class CreateVote(BaseModel):
    post_id: int
    direction: conint(le=1)
