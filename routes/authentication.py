from fastapi import APIRouter, Depends, HTTPException, Request
from config.db import get_db
from sqlalchemy.orm import Session
from services.users import authenticate_user, Login, Register, create_user
from utils.exceptions import NotFound
router = APIRouter(
    prefix="/auth"
)


@router.post("/register")
def register_user(_: Request, user: Register, db: Session = Depends(get_db)):
    try:
        new_user = create_user(user, db)
        return new_user
    except NotFound as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login_user(_: Request, login: Login, db: Session = Depends(get_db)):
    try:
        token = authenticate_user(login, db)
        return {
            "access_token": token,
            "token_type": "bearer", 
            "success": True
        }
    except NotFound as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    