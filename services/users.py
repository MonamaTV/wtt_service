from pydantic import EmailStr
from sqlalchemy.orm import Session
from config.models import User, Score
from utils.exceptions import NotFound, HTTPError
from config.db import get_db
from utils.password import verify_password, hash_password
from utils.sending import *
from typing import Annotated, Dict, List
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from os import getenv
from fastapi.encoders import jsonable_encoder
from config.schemas import Register, Login, UserModel
from datetime import datetime, timedelta

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_user_verify_token(user_data: Dict):
    to_encode = user_data.copy()
    encoded_token = jwt.encode(to_encode, getenv(
        "VERIFY_KEY"), algorithm=getenv("HASH_ALGO"))
    return encoded_token


def create_user(user: Register, db: Session):
    exception = HTTPException(
        status_code=400,
        detail="Passwords do not match.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Verify a wethinkcode email.
    email_split = user.email.split("@")
    if email_split[1].lower() != "student.wethinkcode.co.za":
        raise HTTPException(status_code=400, detail="Invalid WeThinkCode email")

    if email_split[0][-3:] != "023":
        raise HTTPException(status_code=400, detail=f"Cohort {email_split[0][-3:]} not permitted")

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise NotFound("User already exists.")

    if user.password != user.confirm_password:
        raise exception

    hashed_password = hash_password(user.password)
    # TODO: Remove the verified field, and uncomment back the send email part
    updated_user = {
        **user.model_dump(exclude_none=True), "password": hashed_password, "verified": True}
    del updated_user["confirm_password"]

    new_user = User(**updated_user)
    db.add(new_user)
    db.commit()

    token = create_user_verify_token({
        "email": user.email,
        "user_id": new_user.id
    })
    # send_email(user.email, email_split[0], token)

    return new_user


def authenticate_user(login: Login, db: Session):
    user = db.query(User).filter(User.email == login.email).first()
    if user is None:
        raise NotFound("User does not exist.")
    if not verify_password(user.password, login.password):
        raise NotFound("Email or password is incorrect.")
    if user.verified is False:
        raise NotFound("You must verify your account first. Check emails.")

    token = create_user_access_token({
        "email": user.email,
        "user_id": jsonable_encoder(user.id)
    })
    return token


def create_user_access_token(user_data: Dict):
    to_encode = user_data.copy()
    expires_in = int(getenv("ACCESS_TOKEN_EXPIRE_HOURS"))
    to_encode["exp"] = datetime.now() + timedelta(hours=expires_in)
    print(to_encode)
    encoded_token = jwt.encode(to_encode, getenv(
        "SECRET_KEY"), algorithm=getenv("HASH_ALGO"))
    return encoded_token


def get_user_token(token: Annotated[str, Depends(oauth2)]):
    credentials_exception = HTTPException(
        status_code=404,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded_token = jwt.decode(token, getenv(
            "SECRET_KEY"), algorithms=[getenv("HASH_ALGO")])
    except JWTError as e:
        print(e)
        raise credentials_exception
    return decoded_token


def get_user(decoded_token: Dict[str, any], db: Session):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id, email = decoded_token.get("user_id"), decoded_token.get("email")

    user = db.query(User).filter(
        User.email == email, User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_logged_in_user(token: Annotated[str, Depends(oauth2)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=403,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded_token = jwt.decode(token, getenv("SECRET_KEY"), algorithms=[getenv("HASH_ALGO")])
        user_id, email = decoded_token.get("user_id"), decoded_token.get("email")
    except JWTError as e:
        raise credentials_exception

    user = db.query(User).filter(
        User.email == email, User.id == user_id, User.verified == True).first()

    if user is None:
        raise credentials_exception
    return user


def update_user(user, new_details: UserModel, db: Session):
    exception = HTTPException(
        status_code=400,
        detail="Failed to update user",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_to_update = db.query(User).filter(
        User.email == user.email, User.id == user.id
    ).first()

    if user_to_update is None:
        raise exception

    for key, value in new_details.model_dump(exclude_none=True).items():
        if value:
            setattr(user_to_update, key, value)

    # Commit the updates
    db.commit()
    db.refresh(user_to_update)

    return user_to_update


def verify_user(token: str, db: Session):
    exception = HTTPException(
        status_code=400,
        detail="Failed to verify user",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        decoded_token = jwt.decode(token, getenv("VERIFY_KEY"), algorithms=[getenv("HASH_ALGO")])
        user_id, email = decoded_token.get("user_id"), decoded_token.get("email")
    except JWTError as e:
        raise exception

    user_to_verify = db.query(User).filter(
        User.email == email, User.id == user_id
    ).first()

    if user_to_verify is None:
        raise exception

    setattr(user_to_verify, "verified", True)

    # Commit the updates
    db.commit()
    db.refresh(user_to_verify)

    token = create_user_access_token({
        "email": user_to_verify.email,
        "user_id": jsonable_encoder(user_to_verify.id)
    })
    return token


def deactivate_user():
    pass


def get_users_by_email(emails: List[EmailStr], db: Session):
    results = db.query(User).filter(User.email.in_(emails)).all()
    return results


def get_user_by_email(email: EmailStr, db: Session):
    user = db.query(User).filter(User.email == email).first()
    return user


def get_user_stats(user_name: str, db: Session):
    user_email = user_name.lower() + "@student.wethinkcode.co.za"
    scores_user = (db.query(Score).join(User)
                   .filter(User.email == user_email)
                   .order_by(Score.played_at)
                   .limit(10)
                   .all())
    print([score.user for score in scores_user])

    if scores_user is None:
        raise HTTPError(status_code=404, detail="Could not find users scores")
    return scores_user
