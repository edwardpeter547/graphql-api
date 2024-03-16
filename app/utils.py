import os
import random
import jwt
from datetime import datetime
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from graphql import GraphQLError
from app.db.database import Session
from app.db.models import User
from app.settings.config import ADMIN_ROLES
from dotenv import load_dotenv

load_dotenv()

TOKEN_EXPIRATION_TIME_MINUTES = int(os.getenv("TOKEN_EXPIRATION_TIME_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def generate_token(email):

    token_expiration = datetime.utcnow() + timedelta(
        minutes=TOKEN_EXPIRATION_TIME_MINUTES
    )

    payload = {"sub": email, "exp": token_expiration}

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def hash_password(password):
    ph = PasswordHasher()
    return ph.hash(password)


def verify_password(password_hash, password):
    ph = PasswordHasher()
    try:
        ph.verify(password_hash, password)
    except VerifyMismatchError:
        raise GraphQLError("Invalid Password")


def get_authenticated_user(context):
    request = context.get("request")
    auth_header = request.headers.get("Authorization")
    if auth_header:
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            if datetime.now(tz=timezone.utc) > datetime.fromtimestamp(
                payload["exp"], tz=timezone.utc
            ):
                raise GraphQLError("Token has expired")
            user = (
                Session().query(User).filter(User.email == payload.get("sub")).first()
            )
            if not user:
                raise GraphQLError("Could not authenticate user")

            return user
        except DecodeError:
            raise GraphQLError("Invalid authentication token")
    else:
        raise GraphQLError("You must be logged In")


def admin_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        info = args[1]
        user = get_authenticated_user(info.context)
        if user.role not in ADMIN_ROLES:
            raise GraphQLError("You are not authorized to perform this action")
        return func(*args, **kwargs)

    return wrapper


def is_authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        info = args[1]
        try:
            get_authenticated_user(info.context)
        except Exception as ex:
            raise GraphQLError("User must be authenticated to perform this operation.")
        return func(*args, **kwargs)

    return wrapper


def generate_reference():
    today = datetime.now()
    return f"J{today.year}O{today.month}B{random.randint(1000, 10000)}"
