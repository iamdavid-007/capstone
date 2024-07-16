from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from auth import pwd_context
import crud, schemas, auth
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()


# CREATE USERS ENDPOINT
@app.post("/users/", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session=Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    hashed_password = pwd_context.hash(user.password)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user, hashed_password=hashed_password)

# GET MOVIES
# @app.get("/movies/", response_model=list[schemas.Movie])
# def read_movies(skip: int=0, limit: int=10, db: Session=Depends(get_db)):
#     movies = crud.get_movies(db, skip=skip, limit=limit)
#     return {'message': 'success', 'data': movies}
