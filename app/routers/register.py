from fastapi import APIRouter, HTTPException, status, Depends
from starlette.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN
from ..models import User
from ..schemas.register_login_schema import PostRegister, UserRegister
from sqlalchemy.orm import Session
from ..security.passwords import get_password_hash
from ..db.database import create_connection
import re

rx_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

router = APIRouter(
    prefix="/register",
    tags=["Register"]
)


def check_email_is_taken(mail: str, db: Session = Depends(create_connection)):
    retval = db.query(User).filter(User.email == mail).first()
    if retval is None:
        return False
    return True


def check_password_length(pwd: str):
    if len(pwd) <= 3:
        return True

    return False


async def check_email_validity(email: str):
    if re.fullmatch(rx_email, email):
        return False

    return True


def check_nickname_length(name: str):
    if len(name) < 2 or len(name) > 25:
        return True
    return False


def check_email_length(email: str):
    if len(email) < 2 or len(email) > 40:
        return True
    return False


@router.post("/", status_code=HTTP_201_CREATED, response_model=PostRegister,
             summary="Registers new user.",
             responses={403: {"description": "Invalid credentials."}})
async def register(user: UserRegister, db: Session = Depends(create_connection)):
    """
        Input parameters:
        - **email**: user's email
        - **first_name**: user's first name
        - **last_name**: user's last name
        - **study_year**: current study year
        - **pwd**: hashed password

        Response values:

        - **email**: user's email
        - **first_name**: user's first name
        - **last_name**: user's last name
        - **permission**: default false
        - **study_year**: current study year
        - **pwd**: hashed password
    """

    if check_password_length(user.password):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Incorrect password.",
        )
    else:
        user.password = get_password_hash(user.password)  # if the password is correct, create hash from user's password

    if await check_email_validity(user.email):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Incorrect email form.",
        )

    if check_email_is_taken(user.email, db):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Email already taken.",
        )

    if check_nickname_length(user.nickname):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="First name has invalid length.",
        )

    if check_email_length(user.email):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Email has invalid length.",
        )

    registered_user = User(**user.dict())  # wrap json into the model object
    db.add(registered_user)
    db.commit()
    db.refresh(registered_user)

    return registered_user
