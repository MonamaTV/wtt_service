from fastapi import APIRouter, Request, Depends
from services.scores import get_scores_by_user, create_score, ScoreModel, add_competition_score
from services.users import get_logged_in_user
from sqlalchemy.orm import Session
from config.db import get_db
from utils.exceptions import NotFound, HTTPError
from uuid import UUID


router = APIRouter(
    prefix="/scores"
)


@router.get("/")
def get_user_scores(_: Request, limit: int = 10,
                    sort: int = 1,
                    current_user=Depends(get_logged_in_user),
                    db: Session = Depends(get_db)):
    try:
        query = {
            "limit": limit,
            "sort": sort
        }
        scores = get_scores_by_user(current_user, query, db)
        return scores
    except NotFound as e:
        raise HTTPError(status_code=400, detail=str(e))


@router.post("/")
def add_new_score(_: Request, score: ScoreModel, current_user=Depends(get_logged_in_user), db: Session = Depends(get_db)):
    try:
        print("Before Creating score")

        new_score = create_score(current_user, score, db)
        return new_score
    except NotFound as e:
        print("Creating score exception")

        raise HTTPError(status_code=400, detail=str(e))


@router.post("/{competition_id}")
def add_new_score(_: Request, competition_id: str,
                  score: ScoreModel, current_user=Depends(get_logged_in_user), db: Session = Depends(get_db)):
    try:
        new_score = create_score(current_user, score, db)
        updated_comp = add_competition_score(current_user, UUID(competition_id), new_score.id, db)
        return updated_comp
    except NotFound as e:
        print("Creating score exception")
        raise HTTPError(status_code=400, detail=str(e))
