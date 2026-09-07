from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password before storing it.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against its stored hash.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ============================================================
# JWT CONFIGURATION
# ============================================================

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15

REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============================================================
# CREATE ACCESS TOKEN
# ============================================================

def create_access_token(
    user_id: int,
) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ============================================================
# CREATE REFRESH TOKEN
# ============================================================

def create_refresh_token(
    user_id: int,
) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ============================================================
# DECODE ACCESS TOKEN
# ============================================================

def decode_access_token(
    token: str,
) -> dict | None:

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != "access":
            return None

        return payload

    except JWTError:
        return None


# ============================================================
# DECODE REFRESH TOKEN
# ============================================================

def decode_refresh_token(
    token: str,
) -> dict | None:

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != "refresh":
            return None

        return payload

    except JWTError:
        return None