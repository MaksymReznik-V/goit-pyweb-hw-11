from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from database import get_db
from sqlalchemy.orm import Session
from jose import jwt
from dotenv import load_dotenv
import os
import models

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")


ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def hash_password(password: str):
    """
    Hash a plain-text password.

    Args:
        password: Plain-text password provided by the user.

    Returns:
        str: Hashed password generated using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """
    Verify a plain-text password against its stored hash.

    Args:
        plain_password: Plain-text password to verify.
        hashed_password: Previously hashed password.

    Returns:
        bool: True if the password matches the hash, otherwise False.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """
    Create a JWT access token.

    The token contains the provided payload, an expiration time,
    and the ``access`` token type.

    Args:
        data: Data to encode into the JWT token.

    Returns:
        str: Encoded JWT access token.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire, 'type': 'access'})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    """
    Create a JWT refresh token.

    Args:
        data: Data to encode into the JWT token.

    Returns:
        str: Encoded JWT refresh token.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc)+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get the currently authenticated user from an access token.

    The function decodes the JWT token, verifies that it is an
    access token, extracts the user identifier and retrieves the
    corresponding user from the database.

    Args:
        token: JWT access token obtained from the Authorization header.
        db: SQLAlchemy database session.

    Returns:
        models.User: Authenticated user.

    Raises:
        HTTPException: If the token is invalid, has an incorrect type,
            or the user does not exist.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type"
            )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    db_user = db.query(models.User).filter(
        models.User.id == int(user_id)
    ).first()

    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return db_user

def create_email_token(data: dict):
    """
    Create a JWT token for email verification.

    The verification token is valid for 24 hours.

    Args:
        data: Data to encode into the verification token.

    Returns:
        str: Encoded JWT email verification token.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(hours=24)

    to_encode.update({
        "exp": expire,
        "type": "email_verification"
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def verify_email_token(token: str):
    """
    Verify an email verification JWT token.

    Args:
        token: JWT email verification token.

    Returns:
        str | None: Subject stored in the token if it is valid,
        otherwise None.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "email_verification":
            return None

        return payload.get("sub")

    except Exception:
        return None