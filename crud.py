import models
import schemas
from models import Movie, Rating, Comment
from schemas import MovieUpdate, RatingCreate
from fastapi import HTTPException
from sqlalchemy.orm import Session


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_movie(db: Session, movie: schemas.MovieCreate, user_id: int): 
    db_movie = models.Movie(
        **movie.model_dump(exclude_unset=True, exclude_none=True),
        owner_id=user_id
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


def get_movies(db: Session, skip: int=0, limit: int=10):
    return db.query(models.Movie).offset(skip).limit(limit).all()

def get_movie_by_id(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()

def update_movie(db: Session, movie_id: int, movie_update: schemas.MovieUpdate):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise None
    
    if movie_update.title is not None:
        movie.title = movie_update.title
    if movie_update.description is not None:
        movie.description = movie_update.description
    
    # commit the changes to the database
    db.commit()
    db.refresh(movie)
    return movie

def delete_movie(db: Session, movie_id: int) -> bool:
    try:
        movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
        if not movie:
            return False
        db.delete(movie)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"An error occured in the process of deleting movie{e}")
        return False


def create_rating(db: Session, rating: schemas.RatingCreate, user_id: int):
    db_rating = models.Rating(**rating.dict(), user_id=user_id)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

def get_movie_ratings(db: Session, movie_id: int):
    return db.query(Rating).filter(Rating.movie_id == movie_id).all()

def create_comment(db: Session, comment: schemas.CommentCreate, movie_id: int, user_id: int):
    if comment.parent_comment_id is not None:
        parent_comment = db.query(models.Comment).filter(models.Comment.id == comment.parent_comment_id).first()
        if not parent_comment:
            raise HTTPException(status_code=400, detail="Parent comment not found")
    
    db_comment = models.Comment(
        text=comment.text,
        movie_id=movie_id,
        user_id=user_id,
        parent_comment_id=comment.parent_comment_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_for_movie(db: Session, movie_id: int):
    return db.query(Comment).filter(Comment.movie_id == movie_id).all()

def get_comment_by_id(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()
