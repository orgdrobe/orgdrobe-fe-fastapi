from datetime import datetime, timedelta, timezone
import jwt
from jose import JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from typing import Annotated

from .config import config
from . import models, schemas
from .database import get_db


SECRET_KEY = config["SECRET_KEY"]
ALGORITHM = config["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES =  float(config["ACCESS_TOKEN_EXPIRE_MINUTES"])

db_dependency = Annotated[Session, Depends(get_db)]

oauth_scheme = OAuth2PasswordBearer(tokenUrl='auth/email')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(db: db_dependency, token: str = Depends(oauth_scheme)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"}
    )
    token: schemas.TokenData = verify_access_token(token, credentials_exception)

    try:
        user = db.query(models.User).filter(models.User.id == token.id).one()
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")