from typing import Optional, List
from datetime import date, time
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class ScoreModel(BaseModel):
    user_id: Optional[str] = None
    wpm: Optional[float] = None
    played_at: Optional[date] = None
    words: int = Field(gt=0)
    accuracy: Optional[float] = None
    duration: int  # The duration of the test in seconds
    characters: int = Field(gt=0)
    completed: bool
    errors: Optional[int] = Field(ge=0)


class Login(BaseModel):
    password: Optional[str]
    email: Optional[EmailStr]


class UserModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None


pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"


class Register(UserModel):
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    def name_must_contain_space(cls, value):
        if re.fullmatch(pattern, value) is None:
            raise ValueError('Password is not strong.')
        return value.title()

    confirm_password: str = Field(min_length=8)


class CompetitionModel(BaseModel):
    name: str = Field(min_length=2)
    rounds: int = Field(default=5, gt=1)
    competitors: List[EmailStr]


class Token(BaseModel):
    token: str
