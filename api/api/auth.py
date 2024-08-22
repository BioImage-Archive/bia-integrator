from fastapi import APIRouter, Body

from datetime import datetime, timedelta
from typing import Annotated, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.utils import consteq
from typing import Optional
import uuid

from api import constants
from models.repository import Repository
from models.persistence import User
from models.api import AuthenticationToken, TokenData, AuthResult
import os
import base64

router = APIRouter(prefix="/auth", tags=[constants.OPENAPI_TAG_PRIVATE])

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def validate_secret_token(token):
    # If the token is empty (or short/not b64 due to a bug, e.g. None)
    #   Don't allow any user creation/authentication.
    # Especially important if we deploy readonly instances of the api (where token wouldn't be configured)
    if len(token) < 10:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        base64.b64decode(token, validate=True)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


async def get_user(db: Repository, email: str) -> Optional[User]:
    obj_user = await db.users.find_one({"email": email})

    if obj_user:
        return User(**obj_user)
    else:
        return None


async def create_user(db: Repository, email: str, password_plain: str) -> User:
    user = User(
        email=email,
        password=pwd_context.hash(password_plain),
        uuid=str(uuid.uuid4()),
        version=1,
    )

    await db.users.insert_one(user.model_dump())

    return user


async def authenticate_user(db: Repository, email: str, password: str):
    user = await get_user(db, email)

    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    validate_secret_token(JWT_SECRET_KEY)

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Repository = Depends()
):
    validate_secret_token(JWT_SECRET_KEY)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


@router.post("/token", response_model=AuthenticationToken)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Repository = Depends(),
) -> AuthResult:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    auth_result = AuthResult(access_token=access_token)
    return auth_result


@router.post("/users/register")
async def register_user(
    email: Annotated[str, Body()],
    password_plain: Annotated[str, Body()],
    secret_token: Annotated[str, Body()],
    db: Repository = Depends(),
) -> None:
    user_create_token = os.environ["USER_CREATE_SECRET_TOKEN"]
    validate_secret_token(user_create_token)

    if not consteq(secret_token, user_create_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    await create_user(db, email, password_plain)

    return None
