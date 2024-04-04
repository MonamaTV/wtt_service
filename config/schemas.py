from typing import Optional
from datetime import date, time
from pydantic import BaseModel, EmailStr


class ScoreModel(BaseModel):
    user_id: Optional[str] = None
    wpm: float
    played_at: Optional[date] = None
    words: int
    accuracy: float
    duration: time
    characters: int
    completed: bool


class Login(BaseModel):
    password: str
    email: str


class UserModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class Register(UserModel):
    email: EmailStr
    password: str
    confirm_password: str