import datetime

from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, List
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette import status


from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.utility.database import models
from src.utility.database_wrappers import get_user_by_email_db, create_user_db
from src.utility.responses import CredentialException
from src.utility.database.database import get_db
from src.utility.schemas.User import UserCreate, User

auth_router = APIRouter()

# to get a string like this run: openssl rand -hex 32
SECRET_KEY = "22013516088ae490602230e8096e61b86762f60ba48a535f0f0e2af32e87decd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*16  # 16 Hour Expiration

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    """
    OAuth2 access token object that is sent via HTTP request.
    """
    access_token: str
    token_type: str


class AuthTokenModel(BaseModel):
    email: str


# -------------------------------------------------------------------------------
#
#           OAuth2 Implementation for Server Authentication
#
#           You should not touch this code unless you're sure
#           that you know what you're doing, as changes here can
#           have drastic security consequences server-wide :)
#
# -------------------------------------------------------------------------------


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str, db):
    user = get_user_by_email_db(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise CredentialException()
        token_data = AuthTokenModel(email=email)
    except JWTError:
        raise CredentialException()
    user = get_user_by_email_db(db, email=token_data.email)
    if user is None:
        raise CredentialException()
    return user


def get_current_active_user(current_user=Depends(get_current_user)):
    if current_user.disabled:
        raise CredentialException()

    return current_user


# -------------------------------------------------------------------------------
#
#           User Authentication Helper Methods
#
# -------------------------------------------------------------------------------

def current_user_admin(current_user: User = Depends(get_current_user)):
    return current_user_role(['admin'], current_user)


def current_user_organizer(current_user: User = Depends(get_current_user)):
    return current_user_role(['admin', 'organizer'], current_user)


def current_user_participant(current_user: User = Depends(get_current_user)):
    return current_user_role(['admin', 'organizer', 'participant'], current_user)


def current_user_role(roles: List[str], current_user: User = Depends(get_current_user)):
    """
    Permission Checking Function to be used as a Dependency for API endpoints. This is used as a helper.
    This will either return a User object to the calling method if the user meets the authentication requirements,
    or it will raise a CredentialException and prevent the method that depends on this from continuing.

    :param roles: List of Role names that will have permission granted
    :param current_user: Current User
    :return: User object if user has correct role, else raise CredentialException
    """

    if not current_user.role or current_user.role.name not in roles:
        raise CredentialException()

    return current_user


@auth_router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Logs current user in by validating their credentials and then issuing a new OAuth2 bearer token. This token
    is only valid for a fixed amount of time (ACCESS_TOKEN_EXPIRE_MINUTES) and after this has passed the user
    must log back in again.

    :param form_data: HTTP FormData containing login credentials
    :param db: Database parameter, filled by FastAPI automatically
    :return: {'status': 'success'} with OAuth2 bearer token if login successful, else HTTPException
    """
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": form_data.username}, expires_delta=access_token_expires
    )
    return {
        'detail': 'Successfully Logged In.',
        "access_token": access_token,
        "token_type": "bearer"
    }


@auth_router.post('/new', response_model=User)
def create_account(user: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user account with specified information. No permissions are granted upon account creation
    and an administrator must manually add permissions to an account before it is able to access most endpoints.

    :param user: New user's account information
    :param db: Database parameter, filled by FastAPI automatically
    :return Success if user account added, otherwise failure message and status code
    """

    # Hash Password Before Storing in Database
    user.password = get_password_hash(user.password)

    if db.query(models.UserModel).filter(models.UserModel.email == user.email).first():
        return JSONResponse(
            status_code=400,
            content={
                'detail': 'An account with this email address already exists.',
                'email': user.email
            }
        )

    return create_user_db(db, user)


@auth_router.get("/status", dependencies=[Depends(get_current_active_user)])
def get_login_status():
    """
    Check if the current user is authenticated.

    :return: Success if logged in, else CredentialException
    """

    return {'detail': 'User is Authenticated.'}


@auth_router.get("/profile", response_model=User)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Export the data of the current user to the client.

    :param current_user: Currently logged in user to have data exported. This field is auto filled by the HTTP request
    :return: User profile details, excluding hashed password.
    """

    return current_user


# -------------------------------------------------------------------------------
#
#           Administration and Testing Endpoints
#
# -------------------------------------------------------------------------------


@auth_router.post('/create_admin_account')
def create_admin_account_testing(db: Session = Depends(get_db)):

    if get_user_by_email_db(db, 'admin@email.com'):
        return JSONResponse(
            status_code=400,
            content={
                'detail': 'Admin account already exists. Please log in with provided credentials',
                'credentials': 'email: "admin", Password: "password"'
            }
        )

    create_user_db(db, UserCreate(
        email='admin@email.com',
        first_name='Dashboard',
        last_name='Administrator',
        password=get_password_hash('testpass')
    ))

    return {
        'detail': 'Admin account has been created.',
        'credentials': {
            'username': 'admin@email.com',
            'password': 'testpass'
        }
    }