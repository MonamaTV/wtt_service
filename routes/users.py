from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from config.db import get_db
from services.users import get_logged_in_user, get_user, get_user_token, update_user
from config.schemas import UserModel
from typing import Dict
from utils.exceptions import NotFound, HTTPError

router = APIRouter(
    prefix="/users"
)


@router.get("/me")
def get_user_details(_: Request, current_user=Depends(get_logged_in_user)):
    try:
        return current_user
    except NotFound as e:
        raise HTTPError(status_code=401, detail=str(e)) from e


@router.put("/")
def update_user_details(
        _: Request, user: UserModel,
        current_user=Depends(get_logged_in_user),
        db: Session = Depends(get_db)):
    try:
        updated_user = update_user(current_user, user, db)
        return updated_user
    except Exception as e:
        raise HTTPError(status_code=401, detail=str(e)) from e


@router.delete("/deactivate")
def deactivate_user(_: Request, payload: Dict[str, any] = Depends(get_user_token), db: Session = Depends(get_db)):
    try:
        user = get_user(payload, db)
        return user
    except NotFound as e:
        raise HTTPError(status_code=401, detail=str(e)) from e
