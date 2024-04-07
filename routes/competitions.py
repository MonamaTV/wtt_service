from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from services.users import get_logged_in_user
from services.competitions import create_competition
from config.db import get_db
from utils.exceptions import HTTPError
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
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
    # except HTTPError as e:
    #     raise HTTPError(status_code=400, detail=str(e)) from e
    except RequestValidationError as e:
        print("Here")
        raise HTTPError(status_code=400, detail="Invalid data for competition")
