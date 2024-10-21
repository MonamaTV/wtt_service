from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from config.db import get_db
from services.users import get_logged_in_user, verify_user, get_user, get_user_by_id, get_user_token, update_user, get_user_stats, get_user_by_email
from config.schemas import UserModel, Token
from typing import Dict
from utils.exceptions import NotFound, HTTPError
from uuid import UUID

router = APIRouter(
    prefix="/users"
)


@router.get("/me")
def get_user_details(_: Request, current_user=Depends(get_logged_in_user)):
    try:
        return current_user
    except NotFound as e:
        raise HTTPError(status_code=401, detail=str(e)) from e


@router.post("/verify")
def verify(_: Request, token: Token, db: Session = Depends(get_db)):
    try:
        print(token.token)
        access_token = verify_user(token.token, db)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "success": True
        }
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


@router.get("/stats/{user_id}")
def user_stats(_: Request, user_id: str, db: Session = Depends(get_db)):
    try:
        stats = get_user_stats(UUID(user_id), db)
        return stats
    except NotFound as e:
        raise HTTPError(status_code=401, detail=str(e)) from e


@router.get("/username/{user_id}")
def user_stats(_: Request, user_id: str, db: Session = Depends(get_db)):
    try:
        stats = get_user_by_id(UUID(user_id), db)
        return stats
    except NotFound as e:
        raise HTTPError(status_code=401, detail=str(e)) from e
