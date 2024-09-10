from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from services.users import get_logged_in_user
from services.competitions import (
    create_competition,
    get_competitions,
    delete_competition,
    leave_competition,
    user_in_competition,
    add_competitor,
    competition_details,
    competition_information
)
from config.db import get_db
from utils.exceptions import HTTPError
from fastapi.exceptions import RequestValidationError
from config.schemas import CompetitionModel
from uuid import UUID

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
        add_competitor(current_user, current_user.email, new_competition.id, db)
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


@router.delete("/{competition_id}")
def delete_user_competition(_: Request, competition_id: str,
                            current_user=Depends(get_logged_in_user), db: Session = Depends(get_db)):
    try:
        deleted_competition = delete_competition(current_user, UUID(competition_id), db)
        return deleted_competition
    except HTTPError as e:
        raise HTTPError(status_code=400, detail=f"Failed to delete competition {competition_id}") from e


@router.delete("/remove/{competition_id}")
def exit_competition(_: Request, competition_id: str,
                     current_user=Depends(get_logged_in_user), db: Session = Depends(get_db)):
    try:
        left_competition = leave_competition(current_user, UUID(competition_id), db)
        return left_competition
    except HTTPError as e:
        raise HTTPError(status_code=400, detail="Failed to remove user from competition") from e


@router.post("/invites")
def add_new_competitors():
    pass


@router.get("/check/{competition_id}")
def check_user_competition(_: Request, competition_id: UUID,
                           current_user=Depends(get_logged_in_user), db: Session = Depends(get_db)):
    try:
        user = user_in_competition(current_user, competition_id, db)
        return user
    except HTTPError as e:
        raise HTTPError(status_code=400, detail="User is not in the competition.") from e


@router.get("/{competition_id}")
def get_competition_details(_: Request, competition_id: UUID,
                            current_user=Depends(get_logged_in_user), db: Session = Depends(get_db)):
    try:
        details = competition_details(current_user, competition_id, db)
        return details
    except HTTPError as e:
        raise HTTPError(status_code=400, detail="Error fetching competition details.") from e


@router.get("/info/{competition_id}")
def get_competition_information(_: Request, competition_id: UUID,
                                current_user=Depends(get_logged_in_user), db: Session = Depends(get_db)):
    try:
        information = competition_information(current_user, competition_id, db)
        return information
    except HTTPError as e:
        raise HTTPError(status_code=400, detail="Error fetching competition details.") from e
