from fastapi import APIRouter, Request, Depends
from services.scores import get_scores_by_user, create_score, ScoreModel
from services.users import get_logged_in_user
from sqlalchemy.orm import Session
from config.db import get_db
from utils.exceptions import NotFound, HTTPError


router = APIRouter(
    prefix="/scores"
)


@router.get("/")
def get_user_scores(_: Request, current_user=Depends(get_logged_in_user), db: Session = Depends(get_db)):
    try:
        scores = get_scores_by_user(current_user, db)
        return scores
    except NotFound as e:
        raise HTTPError(status_code=400, detail=str(e))


@router.post("/")
def add_new_score(_: Request, score: ScoreModel, current_user=Depends(get_logged_in_user), db: Session = Depends(get_db)):
    try:
        new_score = create_score(current_user, score, db)
        return new_score
    except NotFound as e:
        raise HTTPError(status_code=400, detail=str(e))
