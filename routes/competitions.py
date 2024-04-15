from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from services.users import get_logged_in_user
from services.competitions import create_competition, get_competitions
from config.db import get_db
from utils.exceptions import HTTPError
from fastapi.exceptions import RequestValidationError
from config.schemas import CompetitionModel

router = APIRouter(
    prefix="/competitions"
)


@router.post("/")
def create_new_competition(_: Request,
                           competition: CompetitionModel,
                           current_user=Depends(get_logged_in_user),
                           db: Session = Depends(get_db)):
    try:
        new_competition = create_competition(current_user, competition, db)
        return new_competition
    except HTTPError as e:
        raise HTTPError(status_code=400, detail=str(e)) from e
    except RequestValidationError as e:
        raise HTTPError(status_code=400, detail="Invalid data for competition")


@router.get("/")
def get_user_competitions(_: Request,
                          current_user=Depends(get_logged_in_user),
                          db: Session = Depends(get_db)):
    try:
        competitions = get_competitions(current_user, db)
        return competitions
    except HTTPError as e:
        raise HTTPError(status_code=400, detail="Failed to get user competitions") from e


@router.delete("/")
def delete_user_competition():
    pass


@router.post("/remove")
def leave_competition():
    pass


@router.post("/invites")
def add_new_competitors():
    pass


@router.get("/")
def get_competition_details():
    pass
