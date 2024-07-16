from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


# User Schemas
class UserBase(BaseModel):
    username: str
    full_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# Movie Schemas


class MovieBase(BaseModel):
    title: str
    description: str


class MovieCreate(MovieBase):
    pass


class Movie(MovieBase):
    id: int
    owner_id: int
    owner: User

    class Config:
        orm_mode = True


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

# Rating Schemas


class RatingBase(BaseModel):
    stars: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class RatingCreate(RatingBase):
    pass


class Rating(RatingBase):
    id: int
    movie_id: int
    movie: Movie

    class Config:
        orm_mode = True

# Comment Schemas


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    parent_comment_id: Optional[int] = None


class Comment(CommentBase):
    id: int
    movie_id: int
    movie: Movie
    parent_comment_id: Optional[int] = None
    children: List['Comment'] = []

    class Config:
        orm_mode = True


# This is necessary to handle the nested Comment serialization properly
Comment.update_forward_refs()
