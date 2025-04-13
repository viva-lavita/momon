from datetime import timedelta
from typing import Annotated, Any
from fastapi import APIRouter, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException

from src.auth import constants, exceptions
from src.auth.dependencies import TokenDep
from src.db import SessionDep
from src.schemas import Message
from src.auth.utils import (
    create_access_token,
    generate_password_reset_token,
    generate_reset_password_email,
    get_password_hash,
    verify_password_reset_token,
)
from src.config import settings
from src.auth.schemas import NewPassword, Token
from src.auth.dependencies import authenticate_user
from src.users.dependencies import CurrentUser, get_current_active_superuser
from src.users.schemas import UserPublic
from src.users.service import UserCRUD
from src.utils import send_email


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/access-token", response_model=Token)
async def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(**exceptions.IncorrectUsernameOrPasswordException().dict())
    if not user.is_active:
        raise HTTPException(
            **exceptions.InactiveUserException(
                status_code=status.HTTP_403_FORBIDDEN
            ).dict()
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/test-token", response_model=UserPublic)
async def test_token(current_user: CurrentUser, token: TokenDep) -> Any:
    return current_user


@router.post("/password-recovery/{email}", response_model=Message)
async def recover_password(email: str, session: SessionDep):
    """
    Password Recovery
    """
    user = await UserCRUD.get_by_email(session=session, email=email)

    if not user:
        raise HTTPException(**exceptions.UserNotFoundException().dict())
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message=constants.PASSWORD_RECOVERY_EMAIL_SENT)


@router.post("/reset-password/")
async def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    username = verify_password_reset_token(token=body.token)
    if not username:
        raise HTTPException(**exceptions.InvalidTokenException().dict())
    user = await UserCRUD.get_by_username(session=session, username=username)
    if not user:
        raise HTTPException(**exceptions.UserNotFoundException().dict())
    elif not user.is_active:
        raise HTTPException(
            **exceptions.InactiveUserException(
                status_code=status.HTTP_400_BAD_REQUEST
            ).dict()
        )
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    await session.commit()
    return Message(message=constants.PASSWORD_UPDATED_SUCCESSFULLY)


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
async def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    user = await UserCRUD.get_by_email(session=session, email=email)

    if not user:
        raise HTTPException(**exceptions.UserNotFoundException().dict())
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
