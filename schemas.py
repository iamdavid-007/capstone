from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

# Movie Schemas


class MovieBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MovieCreate(MovieBase):
    pass


class Movie(MovieBase):
    id: int
    owner_id: int
    owner: User

    model_config = ConfigDict(from_attributes=True)


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

# Rating Schemas


class RatingCreate(BaseModel):
    stars: int
    comment: Optional[str] = None
    movie_id: int

    @field_validator('stars')
    def validate_stars(cls, v):
        if not (0 <= v <= 5):
            raise ValueError('Stars must be between 0 and 5')
        return v

class Rating(BaseModel):
    id: int
    stars: int
    comment: Optional[str] = None
    movie_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

# Comment Schemas


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    parent_comment_id: Optional[int] = None


class Comment(CommentBase):
    id: int
    movie_id: int
    parent_comment_id: Optional[int] = None
    children: Optional[List['Comment']] = None

    model_config = ConfigDict(from_attributes=True)


# This is necessary to handle the nested Comment serialization properly
Comment.model_rebuild()
