from typing import Optional
from datetime import datetime, timedelta

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

JWT_SECRET = "d8201edc7657b702278859c5e26f44ca02722f5832ecc0dff9bc970c658f509a"
JWT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def credentials_exception(msg: str):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=msg,
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None, typ: Optional[str] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    if typ:
        to_encode.update({"typ": typ})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_admin_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        public_id: str = payload.get("sub")
        if public_id is None:
            raise credentials_exception("Invalid token")
        is_admin: bool = payload.get("admin")
        if is_admin is None or is_admin is False:
            raise credentials_exception("Invalid admin token")
    except JWTError:
        raise credentials_exception("Missing token")
    return public_id


async def get_jwt_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        public_id: str = payload.get("sub")
        if public_id is None:
            raise credentials_exception("Invalid token")
    except JWTError:
        raise credentials_exception("Missing token")
    return public_id


async def get_refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        typ: str = payload.get("typ")
        if typ != "refresh":
            raise credentials_exception("Refresh token expected")

        jti: str = payload.get("jti")
        if jti is None:
            raise credentials_exception("Token id expected")

        return payload
    except JWTError:
        raise credentials_exception("Missing token")
