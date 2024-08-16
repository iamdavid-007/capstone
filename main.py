import crud, schemas, auth
from typing import Optional, List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from auth import pwd_context, authenticate_user, create_access_token, get_current_user
from database import Base, engine, get_db
from logging_config import logger
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

Base.metadata.create_all(bind=engine)

app = FastAPI()


# Custom Exception Handler for HTTP Exceptions
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP Exception occurred: {exc.detail} - Status Code: {exc.status_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Custom Exception Handler for Request Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()} - Body: {await request.json()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Custom Exception Handler for Generic Errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error occurred: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI app!"}

# CREATE USERS ENDPOINT
@app.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session=Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    hashed_password = pwd_context.hash(user.password)
    if db_user:
        logger.warning("Attempted signup with existing username: %s", user.username)
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(user.password)
    new_user = crud.create_user(db=db, user=user, hashed_password=hashed_password)
    logger.info("User signed up successfully: %s", user.username)
    return new_user

# USERS LOGIN ENDPOINT
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning("Attempted login with Incorrect username or password")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers= {"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={"sub": user.username})
    logger.info("User logged in successfully: %s", user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# USERS LIST  MOVIE ENDPOINT {AUTHENTICATED ACCESS}
@app.post("/movies")
def create_movie(movie: schemas.MovieCreate, user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        new_movie = crud.create_movie(
            db=db,
            movie=movie,
            user_id=user.id
        )
        logger.info("Movie listed successfully: %s by user %s", movie.title, user.username)
        return new_movie
    except Exception as e:
        logger.error("Failed to list movie: %s. Error: %s", movie.title, str(e))
        raise HTTPException(status_code=500, detail="Failed to list movie")


# VIEW ALL MOVIES {public access}
@app.get("/movies/")
def get_movies(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    movies = crud.get_movies(
        db
    )
    logger.info("Movies retrieved: %d", len(movies))
    return movies

# GET A MOVIE {public access}
@app.get("/movie/{movie_id}", response_model=schemas.Movie)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if not movie:
        logger.warning("Attempted getting movie that does not exist")
        raise HTTPException(status_code=404, detail="Movie not found")
    logger.info("Movie retrieved successfully")
    return movie

# Edit a movie (only by the user who listed it)
@app.put("/movies/{movie_id}", response_model=schemas.Movie)
def update_movie(
    movie_id: int,
    movie_update: schemas.MovieUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    movie = crud.get_movie_by_id(db, movie_id)
    if not movie:
        logger.warning("Movie not found for update: %d", movie_id)
        raise HTTPException(status_code=404, detail="Movie not found")
    if movie.owner_id != current_user.id:
        logger.warning("Unauthorized update attempt by user %s for movie %d", current_user.username, movie_id)
        raise HTTPException(status_code=403, detail="Not authorized to update this movie")
    updated_movie = crud.update_movie(db=db, movie_id=movie_id, movie_update=movie_update)
    logger.info("Movie updated successfully: %d by user %s", movie_id, current_user.username)
    return updated_movie


# Delete a movie (only by the user who listed it)
@app.delete("/movies/{movie_id}")
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    movie = crud.get_movie_by_id(db, movie_id)
    if not movie:
        logger.warning("Movie not found for deletion: %d", movie_id)
        raise HTTPException(status_code=404, detail="Movie not found")
    if movie.owner_id != current_user.id:
        logger.warning("Unauthorized delete attempt by user %s for movie %d", current_user.username, movie_id)
        raise HTTPException(status_code=403, detail="Not authorized to delete movie")
    
    if not crud.delete_movie(db=db, movie_id=movie_id):
        raise HTTPException(status_code=500, detail="failed to delete movie")
    logger.info("Movie deleted successfully: %d by user %s", movie_id, current_user.username)
    return {"Movie Deleted Successfully"}


# Rate a movie (authenticated access)

@app.post("/movies/{movie_id}/rate", response_model=schemas.Rating)
def rate_movie(
    movie_id: int,
    rating: schemas.RatingCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_movie = crud.get_movie(db, movie_id)
    if not db_movie:
        logger.warning("Movie not found when attempting to rate: movie_id=%d", movie_id)
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # No need to compare rating.movie_id with movie_id if we are passing movie_id directly in the URL
    db_rating = crud.create_rating(db=db, rating=rating, user_id=current_user.id)
    logger.info("Movie rated successfully: movie_id=%d, user_id=%d, stars=%d", movie_id, current_user.id, rating.stars)
    return db_rating

# Get ratings for a movie
@app.get("/movies/{movie_id}/ratings/", response_model=List[schemas.Rating])
def get_movie_ratings(movie_id: int, db: Session = Depends(get_db)):
    ratings = crud.get_movie_ratings(db=db, movie_id=movie_id)
    logger.info("Retrieved %d ratings for movie_id=%d", len(ratings), movie_id)
    return ratings

# Add a comment to a movie (authenticated access)
@app.post("/movies/{movie_id}/comments", response_model=schemas.Comment)
def add_comment(
    movie_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    movie = crud.get_movie(db, movie_id)
    if not movie:
        logger.warning("Attempted to add comment to non-existent movie: movie_id=%d", movie_id)
        raise HTTPException(status_code=404, detail="Movie not found")
    db_comment = crud.create_comment(db=db, comment=comment, movie_id=movie_id, user_id=current_user.id)
    logger.info("Comment added to movie: movie_id=%d, user_id=%d, comment_id=%d", movie_id, current_user.id, db_comment.id)
    return db_comment

# View comments for a movie (public access)
@app.get("/movies/{movie_id}/comments", response_model=List[schemas.Comment])
def view_comments(movie_id: int, db: Session = Depends(get_db)):
    comments = crud.get_comments_for_movie(db=db, movie_id=movie_id)
    logger.info("Retrieved %d comments for movie_id=%d", len(comments), movie_id)
    return comments

# Add comment to a comment i.e nested comments (authenticated access)
@app.post("/comments/{comment_id}/reply", response_model=schemas.Comment)
def reply_to_comment(
    comment_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    parent_comment = crud.get_comment_by_id(db, comment_id)
    if not parent_comment:
        logger.warning("Attempted to reply to non-existent comment: comment_id=%d", comment_id)
        raise HTTPException(status_code=404, detail="parent comment not found")
    
    db_comment = crud.create_comment(db=db, comment=comment, movie_id=parent_comment.movie_id, user_id=current_user.id)
    logger.info("Reply added to comment: parent_comment_id=%d, user_id=%d, reply_comment_id=%d", comment_id, current_user.id, db_comment.id)
    return db_comment
