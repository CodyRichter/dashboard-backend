from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.routers.auth import auth_router
from src.routers.prizes import prize_router
from src.routers.roles import role_router
from src.utility.database import models
from src.utility.database.database import engine
from src.utility.responses import CredentialException, PrizeNotFoundException, ProjectNotFoundException, \
    RoleNotFoundException, UserNotFoundException

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
    responses={404: {"detail": "Not found"}},
)


app.include_router(
    prize_router,
    prefix="/prizes",
    tags=["prizes"],
    responses={404: {"detail": "Not found"}},
)

app.include_router(
    role_router,
    prefix="/roles",
    tags=["roles"],
    responses={404: {"detail": "Not found"}},
)


@app.exception_handler(CredentialException)
async def credential_exception_handler(request: Request, exc: CredentialException):
    """
    Handler for credential exception. This type of exception is raised when a client attempts to access an endpoint
    without sufficient permissions for endpoints that are protected by OAuth2. This exception is raised if the client
    has no bearer token, if the bearer token is expired, or if their account does not have sufficient permissions/roles
    to access a certain endpoint.
    :param request: HTTP Request object
    :param exc: Exception
    :return: 401 HTTP Exception with authentication failure message
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": "Access Denied. You may not be logged in, or your role "
                      "does not have sufficient permission to access this page."
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(PrizeNotFoundException)
async def prize_exception_handler(request: Request, exc: PrizeNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": "Unable to find prize with given criteria."
        },
    )


@app.exception_handler(ProjectNotFoundException)
async def project_exception_handler(request: Request, exc: ProjectNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": "Unable to find project with given criteria."
        },
    )


@app.exception_handler(RoleNotFoundException)
async def project_exception_handler(request: Request, exc: RoleNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": "Unable to find role with given criteria."
        },
    )

@app.exception_handler(UserNotFoundException)
async def project_exception_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": "Unable to find user with given criteria."
        },
    )



@app.get("/")
async def root():
    return {
        "detail": "Dashboard is Running!"
    }