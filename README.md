# Movie Rating and Commenting System

This project implements a web application for movie enthusiasts to rate and comment on movies. It provides functionalities for user authentication, movie listing, rating, and commenting. This README provides an overview of the project structure, setup instructions, and usage details.

## Features

- **User Authentication:**
  - User registration with username, email, and password.
  - JWT token generation for secure authentication.
  - User login with JWT-based authentication.

- **Movie Management:**
  - List movies (authenticated users only).
  - View all movies (public access).
  - Edit and delete movies (only by the user who listed them).

- **Movie Rating:**
  - Rate movies with a star rating (authenticated access).
  - Retrieve average ratings for a movie.

- **Comments:**
  - Add comments to movies (authenticated access).
  - View comments for a movie.

## Technologies Used

- **Backend Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT (JSON Web Tokens)
- **Password Hashing:** Bcrypt
- **API Documentation:** Swagger UI and ReDoc

## Project Structure
├── app
│ ├── api
│ │ ├── auth.py # User authentication routes
│ │ ├── movies.py # Movie CRUD operations
│ │ └── comments.py # Comment CRUD operations
│ ├── models.py # SQLAlchemy models (User, Movie, Rating, Comment)
│ ├── schemas.py # Pydantic schemas for data validation
│ ├── crud.py # CRUD operations for database interactions
│ ├── database.py # Database connection and setup
│ ├── main.py # FastAPI application setup
│ ├── auth.py # JWT token creation and authentication
│ ├── utils.py # Utility functions
│ └── .env # Environment variables (not included in repository)
├── migrations # Database migrations (Alembic)
├── tests # Unit tests
├── requirements.txt # Python dependencies
└── README.md # Project overview and setup instructions

## Getting Started

### Prerequisites

- Python 3.7+
- PostgreSQL

1. Clone the repository:

   ```bash
   git clone https://github.com/iamdavid-007/capstone.git
   cd your-repository
   
2. Set up a virtual environment (optional but recommended):
   python -m venv env
   source env/bin/activate   # On Unix/MacOS
   .\env\Scripts\activate    # On Windows

3. Install dependencies:
   pip install -r requirements.txt

4. Set up the database and environment variables:
- Create a PostgreSQL database.
- Create .env in project folder and configure database URL (DB_URL), SECRET_KEY, ALGORITHM, and ACCESS_TOKEN_EXPIRE_MINUTES.

5. Alembic is for Database Migrations
- alembic upgrade head

### Starting the application
Start the FastAPI application:
- uvicorn main:app --reload
- The application will be available at http://127.0.0.1:8000

### API Documentation
- Swagger UI: http://127.0.0.1:8000/docs

### Testing
- Testing with pytest
- pytest

### Testing
- This project is licensed under the MIT License - see the LICENSE file for details.
