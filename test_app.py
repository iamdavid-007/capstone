import pytest, os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from database import Base, get_db
from fastapi import HTTPException
from main import app
import models

# PostgreSQL setup
SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield


# TEST CREATE USERS ENDPOINT
@pytest.mark.parametrize("username, password, full_name, email", [("testuser", "testpass", "Test User", "testuser@example.com")])
def test_signup(client, setup_database, username, password, full_name, email):
    response = client.post("/signup", json={"username": username, "password": password, "full_name": full_name, "email": email})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username


# TEST USERS LOGIN ENDPOINT
@pytest.mark.parametrize("username, password", [("testuser", "testpass")])
def test_login(client, setup_database, username, password):
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# TEST USERS LIST  MOVIE ENDPOINT {AUTHENTICATED ACCESS}
@pytest.mark.parametrize("username, password", [("testuser", "testpass")])
def test_create_movie(client, setup_database, username, password):
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create a movie
    movie_data = {"title": "Test Movie 2", "description": "A test movie description 2"}
    response = client.post("/movies", json=movie_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Movie 2"


# TEST VIEW ALL MOVIES {public access}
@pytest.mark.parametrize("username, password", [("testuser", "testpass")])
def test_view_all_movies(client, setup_database, username, password):
    # Login to get a token
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    print("============")
    token = response.json()["access_token"]

    # View all movies without authentication (public access)
    response = client.get("/movies/")
    assert response.status_code == 200
    movies = response.json()
    assert len(movies) > 0  # Ensure there are movies in the database

    # Verify one of the movies is the one created earlier
    assert any(movie["title"] == "Test Movie for Deletion" for movie in movies)


# TEST GET A MOVIE {public access}
@pytest.mark.parametrize("movie_id", [1])  # Assuming the movie ID to be tested
def test_get_specific_movie(client, setup_database, movie_id):
    # Get a specific movie by ID (public access)
    response = client.get(f"/movie/{movie_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == movie_id
    assert "title" in data
    assert "description" in data


# TEST Edit a movie (only by the user who listed it)
@pytest.mark.parametrize("username, password", [("testuser4", "testpass4")])
def test_edit_movie(client, setup_database, username, password):
    # Login to get a token
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Edit a movie (only by the user who listed it)
    movie_id = 2  # Assuming the movie ID to be tested
    response = client.put(
        f"/movies/{movie_id}",
        json={"title": "Updated Title", "description": "Updated Description"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"


# Delete a movie (only by the user who listed it)
@pytest.mark.parametrize("username, password", [("testuser4", "testpass4")])
def test_delete_movie(client, setup_database, username, password):
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Delete a movie
    movie_id = 2  # Use an existing movie ID or create one in the setup
    response = client.delete(f"/movies/{movie_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == ["Movie Deleted Successfully"]


# TEST Rate a movie (authenticated access)
@pytest.mark.parametrize("username, password, movie_id, stars, comment", [
    ("testuser", "testpass", 1, 5, "Great movie!")  # Assuming movie ID 1 and a 5-star rating with a comment
])
def test_rate_movie(client, setup_database, username, password, movie_id, stars, comment):
    # Login to get a token
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Rate the movie with the authenticated user
    rating_data = {"movie_id": movie_id, "stars": stars, "comment": comment}
    response = client.post(
        f"/movies/{movie_id}/rate",
        json=rating_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["movie_id"] == movie_id
    assert data["user_id"] is not None  # Ensure a user ID is associated with the rating
    assert data["stars"] == stars
    assert data["comment"] == comment


# TEST Get ratings for a movie
@pytest.mark.parametrize("movie_id", [1])  # Assuming the movie ID to be tested
def test_get_movie_ratings(client, setup_database, movie_id):
    response = client.get(f"/movies/{movie_id}/ratings/")
    assert response.status_code == 200
    ratings = response.json()
    assert isinstance(ratings, list)  # Ensure it returns a list of ratings
    if ratings:  # If there are ratings
        assert all('stars' in rating for rating in ratings)  # Check that 'stars' field is in each rating
        assert all('user_id' in rating for rating in ratings)  # Check that 'user_id' field is in each rating


# TEST Add a comment to a movie (authenticated access)
@pytest.mark.parametrize("username, password, movie_id, text", [
    ("testuser", "testpass", 1, "This is a test comment for the movie")  # Assuming movie ID 1
])
def test_add_comment_to_movie(client, setup_database, username, password, movie_id, text):
    # Login to get a token
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Add a comment to the movie
    comment_data = {"text": text}
    response = client.post(
        f"/movies/{movie_id}/comments",
        json=comment_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == text
    assert data["movie_id"] == movie_id


# TEST View comments for a movie (public access)
@pytest.mark.parametrize("movie_id", [1])
def test_view_comments_for_movie(client, setup_database, movie_id):
    response = client.get(f"/movies/{movie_id}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert isinstance(comments, list)
    if comments:
        assert all('text' in comment for comment in comments)
        assert all('id' in comment for comment in comments)
        assert all('movie_id' in comment for comment in comments)
        assert all('parent_comment_id' in comment for comment in comments)
        assert all('children' in comment for comment in comments)  # If you include 'children' in the response
    else:
        assert comments == []


# TEST View nested comments (public access)
@pytest.mark.parametrize("movie_id", [1])  # Assuming the movie ID to be tested
def test_view_nested_comments(client, setup_database, movie_id):
    response = client.get(f"/movies/{movie_id}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert isinstance(comments, list)  # Ensure it returns a list of comments
    if comments:  # If there are comments
        for comment in comments:
            assert "children" in comment  # Check if nested comments exist
            if comment["children"]:
                assert isinstance(comment["children"], list)  # Nested comments should be a list
