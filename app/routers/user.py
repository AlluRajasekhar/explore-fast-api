from fastapi import Depends, status, HTTPException, APIRouter
from app.schemas import UserOut, CreateUser
from app.utils import hash_password
from app.models import User
from app.database import get_db
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/users", tags=['Users'])


# Create Users
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user : CreateUser, db : Session = Depends(get_db)):

    # Hash user password before writing to database
    hashed_password = hash_password(user.password)
    user.password = hashed_password

    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# Get a specific user by id
@router.get("/{id}", response_model=UserOut)
def get_user(id : int, db : Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post wiht id {id} not found')

    return user