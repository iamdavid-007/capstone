from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Relationships
    movies = relationship("Movie", back_populates="owner")
    ratings = relationship("Rating", back_populates="user")
    comments = relationship("Comment", back_populates="user")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", back_populates="movies")
    ratings = relationship("Rating", back_populates="movie")
    comments = relationship("Comment", back_populates="movie")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stars = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    movie = relationship("Movie", back_populates="ratings")
    user = relationship("User", back_populates="ratings")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(String, nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    parent_comment_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    
    movie = relationship("Movie", back_populates="comments")
    user = relationship("User", back_populates="comments")

    
    parent_comment = relationship(
        "Comment",
        remote_side=id,
        backref=backref("children", cascade="all, delete-orphan")
    )

    def __repr__(self):
        return f"<Comment(id={self.id}, text={self.text}, movie_id={self.movie_id}, parent_comment_id={self.parent_comment_id})>"