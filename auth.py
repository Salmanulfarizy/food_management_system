from datetime import datetime, timedelta

from jose import JWTError, jwt

from passlib.context import CryptContext


SECRET_KEY = "mysecretkey"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# Hash password
def hash_password(password: str):

    return pwd_context.hash(password)


# Verify password
def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# Create JWT token
def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# Verify JWT token
def verify_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        return {
            "error": "Invalid token"
        }