import uuid
from typing import Optional
from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import Config

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(iat=datetime.utcnow(), exp=expire, jti=str(uuid.uuid4()))

    return jwt.encode(claims=to_encode, key=Config.RANDOM_SECRET, algorithm=Config.ALGORITH)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, Config.RANDOM_SECRET, algorithms=[Config.ALGORITH])
        return payload
    except (JWTError, ExpiredSignatureError):
        return None
