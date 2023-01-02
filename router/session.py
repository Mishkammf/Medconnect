

from fastapi import Depends, HTTPException, APIRouter, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from apimodel.security_models import UserToken
from common.database.db_session import get_db
from security.authentication_service import authenticate_user
from services.token_manager import handle_tokens_at_login

router = APIRouter()


@router.post("", response_model=UserToken)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), device: int = Header(0),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username.strip().lower(), form_data.password,
                             form_data.client_id.strip().lower())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    hashed_token = handle_tokens_at_login(db, user, device)

    return {"access_token": hashed_token, "token_type": "bearer", "user_key": user.user_key}
