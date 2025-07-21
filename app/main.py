from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from starlette import status

app = FastAPI(
    description="FastAPI Project with SQLModel - Users API",
)

# --------------------------------------------------------------------------------
# SQLModel Schema for User (DB Model + Response Schema)
# --------------------------------------------------------------------------------

"""
SQLModel schema for User, which represents the user data model.
This schema is used for both database operations and API responses.
"""


class User(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str
    email: str
    age: int
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now, alias="createdAt"
    )


# --------------------------------------------------------------------------------
# DB Setup
# --------------------------------------------------------------------------------

DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)  # Create tables in the database


def get_db():
    with Session(engine) as session:
        yield session


# --------------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------------


@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User, db: Session = Depends(get_db)):
    """
    Create a new user in the database.
    """
    new_user = User(name=user.name, email=user.email, age=user.age)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh to get the ID and other fields
    return new_user


@app.get("/users", response_model=list[User], status_code=status.HTTP_200_OK)
async def root(db: Session = Depends(get_db)):
    """
    Retrieve all users from the database.
    """
    users = db.exec(select(User)).all()
    return users


@app.get("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a user by ID from the database.
    """
    user = db.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in the database",
        )
    return user


@app.put("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: User, db: Session = Depends(get_db)):
    """
    Update an existing user in the database.
    """
    db_user = db.exec(select(User).where(User.id == user_id)).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in the database",
        )
    db_user.name = user.name
    db_user.email = user.email
    db_user.age = user.age
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID from the database.
    """

    db_user = db.exec(select(User).where(User.id == user_id)).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return None
