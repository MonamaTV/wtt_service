from typing import Optional, List
from datetime import date, time
from pydantic import BaseModel, EmailStr, Field


class ScoreModel(BaseModel):
    user_id: Optional[str] = None
    wpm: Optional[float] = None
    played_at: Optional[date] = None
    words: int = Field(ge=0)
    accuracy: Optional[float] = None
    duration: int  # The duration of the test in seconds
    characters: int = Field(ge=0)
    completed: bool
    errors: Optional[int] = None


class Login(BaseModel):
    password: Optional[str]
    email: Optional[EmailStr]


class UserModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class Register(UserModel):
    email: EmailStr
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class CompetitionModel(BaseModel):
    name: str
    competitors: List[EmailStr]
