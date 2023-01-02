
from typing import List

from fastapi import Depends, HTTPException, APIRouter, Header, Response, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from apimodel.security_models import UserToken
from common.database.db_session import get_db
from security.authentication_service import authenticate_user, validate_token, \
    validate, get_current_active_user
from services.token_manager import handle_tokens_at_login

router = APIRouter()


@router.post("", response_model=UserToken)
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 device: int = Header(0),
                                 db: Session = Depends(get_db)):
    if not (form_data.client_id and form_data.username and form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Insufficient data to Authorize",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = authenticate_user(db, form_data.username.strip().lower(), form_data.password,
                             form_data.client_id.strip().lower())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.enable_login:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login disabled for this user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.api_access_only:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only API access is available for this user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    hashed_token = handle_tokens_at_login(db, user, device)
    return {"access_token": hashed_token, "token_type": "bearer", "user_key": user.user_key,
            "first_name": user.first_name, "tenant_id": form_data.client_id,
            "last_name": user.last_name, "user_login_id": user.user_login_id}



@router.get("/validate", response_model=UserToken)
async def validate_token_from_header(x_original_uri: str = Header(None), db: Session = Depends(get_db)):
    """
        Validate token  to authorized actions </br>
        x_original_uri = token=Token_Generated</br>
        ***Return*** : Token and Status
    """
    user = None
    if x_original_uri and "&" in x_original_uri:
        token = x_original_uri.split("&")[0].split("=")[1]
        user = validate_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password or token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": token, "token_type": "bearer", "user_key": user["user_key"]}


@router.post("/page_access")
async def validate_page_access(db: Session = Depends(get_db), roles: List[str] = Body(...),
                               user: {} = Depends(get_current_active_user)):
    """
        Validate Page Access based on application roles
        role : array of permissions to check
    """
    return {"Status": validate(db, user["user_group_key"], roles)}
