from datetime import datetime, timedelta, timezone
import jwt

from .config import config

SECRET_KEY = config["SECRET_KEY"]
ALGORITHM = config["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES =  float(config["ACCESS_TOKEN_EXPIRE_MINUTES"])


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt