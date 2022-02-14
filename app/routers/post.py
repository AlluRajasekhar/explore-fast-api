from turtle import isdown
from fastapi import Depends, Response, status, HTTPException, APIRouter
from app.schemas import PostOut, CreatePost, PostCount
from app.utils import hash_password
from app.models import Post, Vote
from app.database import get_db
from app.oauth2 import get_current_user
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

router = APIRouter(prefix="/posts", tags=['Posts'])

# Get all posts
@router.get("/all", response_model=List[PostCount])
def get_posts(
        db: Session = Depends(get_db), 
        user_id: int = Depends(get_current_user),
        limit: int = 5,
        skip: int = 0,
        search: Optional[str] = ''):
    
    posts = db.query(Post, func.count(Vote.post_id).label('Votes')).join(Vote, Vote.post_id==Post.id, isouter=True).group_by(Post.id).filter(Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

# Get a specific post by id
@router.get("/{id}", response_model=PostOut)
def get_post(id : int, db : Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == id).first()

    post =db.query(Post, func.count(Vote.post_id).label('Votes')).join(Vote, Vote.post_id==Post.id, isouter=True).group_by(Post.id).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} not found')
    return post

# Create Post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostOut, )
def create_posts(post : CreatePost, db : Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    new_post = Post(owner_id = user_id.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

# Delete a specific post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db : Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    post_query = db.query(Post).filter(Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} not found')

    if post.owner_id != int(user_id.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to perform requested action')

    post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update a specific post
@router.put("/{id}", response_model=PostOut)
def update_post(id: int, post : CreatePost, db : Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    post_query = db.query(Post).filter(Post.id == id)
    result = post_query.first()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} not found')

    if result.owner_id != int(user_id.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to perform this action')

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()


