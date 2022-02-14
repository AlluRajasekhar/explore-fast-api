from http.client import HTTPException
from sys import prefix
from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import CreateVote
from app.database import get_db
from app.models import Vote
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session



router = APIRouter(prefix='/vote', tags=['Vote'])

@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: CreateVote, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):

    post = db.query(Vote).filter(Vote.post_id==vote.post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {vote.post_id} not found')
        
    vote_query = db.query(Vote).filter(Vote.post_id==vote.post_id, Vote.user_id==current_user.id)
    found_vote = vote_query.first()

    if vote.direction==1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'User {current_user.id} has already voted on post {vote.post_id}')
        
        new_vote = Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {'message' : 'Successfully added vote'}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vote does nopt exist')

        vote_query.delete(synchronize_session=False)
        db.commit()

        return {'message': 'Successfully deleted vote'}