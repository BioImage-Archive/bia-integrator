from fastapi import APIRouter, Body

from datetime import datetime, timedelta
from typing import Annotated, Union, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.utils import consteq
import uuid

from api.app import get_db, settings
from api import constants
from api.models.repository import Repository
from api.models.persistence import User
from api.models.api import AuthenticationToken, TokenData, AuthResult
import base64


router = APIRouter(prefix="/auth", tags=[constants.OPENAPI_TAG_PRIVATE])

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v2/auth/token")


def validate_secret_token(token):
    # If the token is empty (or short/not b64 due to a bug, e.g. None)
    #   Don't allow any user creation/authentication.
    # Especially important if we deploy readonly instances of the api (where token wouldn't be configured)
    if len(token) < 10:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        # Note for validate=True:
        #   Common placeholder values (ex 00123456789==) raise an 'Excess data after padding' error
        #   because validate=True expects values to already be correctly padded
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
    validate_secret_token(settings.jwt_secret_key)

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Repository, Depends(get_db)],
):
    validate_secret_token(settings.jwt_secret_key)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
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
    db: Annotated[Repository, Depends(get_db)],
) -> AuthResult:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.jwt_ttl_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    auth_result = AuthResult(access_token=access_token)
    return auth_result


@router.post("/user/register")
async def register_user(
    email: Annotated[str, Body()],
    password_plain: Annotated[str, Body()],
    secret_token: Annotated[str, Body()],
    db: Annotated[Repository, Depends(get_db)],
) -> None:
    user_create_token = settings.user_create_secret_token
    validate_secret_token(user_create_token)

    if not consteq(secret_token, user_create_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    await create_user(db, email, password_plain)

    return None


def make_router() -> APIRouter:
    return router
