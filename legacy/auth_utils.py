from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import (
    JWT_SECRET_KEY,
    JWT_REFRESH_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_EXPIRE_MINUTES,
    JWT_REFRESH_EXPIRE_MINUTES,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash & verify passwords

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Internal helper to create tokens (use local system time)

def _create_token(*, data: dict, role: str, expires_delta: timedelta, secret: str, token_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.now() + expires_delta  # local system time per requirement
    to_encode.update({
        "exp": expire,
        "role": role,
        "type": token_type,
    })
    return jwt.encode(to_encode, secret, algorithm=JWT_ALGORITHM)


def create_access_token(data: dict, role: str, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(minutes=JWT_ACCESS_EXPIRE_MINUTES)
    return _create_token(
        data=data, role=role, expires_delta=delta, secret=JWT_SECRET_KEY, token_type="access"
    )


def create_refresh_token(data: dict, role: str, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(minutes=JWT_REFRESH_EXPIRE_MINUTES)
    return _create_token(
        data=data, role=role, expires_delta=delta, secret=JWT_REFRESH_SECRET_KEY, token_type="refresh"
    )


# Token verification

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        if payload.get("sub") is None:
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        if payload.get("sub") is None:
            return None
        return payload
    except JWTError:
        return None
