from sqlalchemy.orm import Session
from config.models import User
from utils.exceptions import NotFound
from config.db import get_db
from utils.password import verify_password, hash_password
from typing import Annotated, Dict
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from os import getenv
from fastapi.encoders import jsonable_encoder
from uuid import UUID
from config.schemas import Register, Login, UserModel


oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_user(user: Register, db: Session):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise NotFound("User already exists.")

    hashed_password = hash_password(user.password)

    updated_user = {
        **user.model_dump(exclude_none=True), "password": hashed_password}
    del updated_user["confirm_password"]

    new_user = User(**updated_user)
    db.add(new_user)
    db.commit()

    return new_user


def authenticate_user(login: Login, db: Session):
    user = db.query(User).filter(User.email == login.email).first()
    if user is None:
        raise NotFound("User does not exist.")
    if not verify_password(user.password, login.password):
        raise NotFound("Email or password is incorrect.")

    token = create_user_access_token({
        "email": user.email,
        "user_id": jsonable_encoder(user.id)
    })
    return token


def create_user_access_token(user_data: Dict):
    to_encode = user_data.copy()
    expires_in = getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    # to_encode.update({"exp": 30})
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
        User.email == email, User.id == UUID(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


def get_logged_in_user(token: Annotated[str, Depends(oauth2)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded_token = jwt.decode(token, getenv("SECRET_KEY"), algorithms=[getenv("HASH_ALGO")])
        user_id, email = decoded_token.get("user_id"), decoded_token.get("email")
    except JWTError as e:
        raise credentials_exception

    user = db.query(User).filter(
        User.email == email, User.id == UUID(user_id)).first()

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
        setattr(user_to_update, key, value)

    # Commit the updates
    db.commit()
    db.refresh(user_to_update)

    return user_to_update


def deactivate_user():
    pass
