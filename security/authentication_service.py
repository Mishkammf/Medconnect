

from datetime import timedelta, datetime

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

import common.global_variables
from common.config_manager import get_config
from common.database.admin import Admin
from common.database.admin_roles import AdminRole
from common.database.db_session import get_db
from common.database.user import User
from common.database.user_role_map import UserRolesUserGroupMap
from common.database.user_roles import UserRole
from common.database.user_token import UserToken
from common.string_constants import user_tenant_string, user_group_key_string, user_key_string, admin_group_key_string, \
    admin_key_string
from exceptions.custom_exceptions import DatabaseException, ConfigNotFoundException
from security.oauth2_scheme import oauth2_scheme
from services.db_crud_operations import retrieve

TOKEN_SALT = "token_salt"
PASSWORD_SALT = "password_salt"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

token_expired_exception = HTTPException(
    status_code=440,
    detail="Token expired",
    headers={"WWW-Authenticate": "Bearer"},
)

NO_PERMISSION_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="No valid permission to access this content",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password + PASSWORD_SALT, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password + PASSWORD_SALT)


def validate_token(token, db):
    try:
        user = db.query(UserToken.token, UserToken.id, UserToken.token_expiry, User.tenant_key, User.user_group_key,
                        User.user_key,
                        User.expire_token, ).join(User).filter(
            and_(User.is_active == True, token == UserToken.token)).first()
        if user is None:
            raise credentials_exception
        user_obj = {user_tenant_string: user.tenant_key, user_group_key_string: user.user_group_key,
                    user_key_string: user.user_key}
        if user.expire_token:
            if datetime.utcnow() < user.token_expiry:
                item = db.query(UserToken).filter(getattr(UserToken, 'id') == user.id).first()
                item.token_expiry = datetime.utcnow() + timedelta(
                    minutes=get_config("token_expiry_minutes"))
                db.commit()
                db.close()
            else:
                raise token_expired_exception
        return user_obj
    except SQLAlchemyError:
        raise DatabaseException


def validate_admin_token(token, db):
    try:
        admin = retrieve(db, Admin, None, and_(Admin.is_active == True, token == Admin.token), [Admin])[0]
        if not admin:
            raise credentials_exception
        admin = admin[0]
        admin_obj = {admin_group_key_string: admin.admin_group_key,
                     admin_key_string: admin.admin_key}

        if datetime.utcnow() < admin.token_expiry:
            admin.token_expiry = datetime.utcnow() + timedelta(
                minutes=int(get_config("token_expiry_minutes")))
            db.commit()
            db.close()
        else:
            raise token_expired_exception
        return admin_obj
    except SQLAlchemyError:
        raise DatabaseException


def delete_token(user_key, db):
    try:
        user = db.query(User).filter(user_key == User.user_key).first()
        user.token = None
        db.commit()

    except SQLAlchemyError:
        raise DatabaseException


# print(get_password_hash("Complexpw!1"))

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return validate_token(token, db)


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user


async def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return validate_admin_token(token, db)


async def get_current_active_admin(current_admin: Admin = Depends(get_current_admin)):
    return current_admin


def authenticate_user(db, username: str, password: str, tenant_id):
    tenant_key = common.global_variables.get_id_from_key(common.global_variables.db_tenant_keys, tenant_id)
    if tenant_key == -1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="TenantID does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user(db, username, tenant_key)
    if not user:
        return False
    if not verify_password(password, user.user_password):
        return False
    return user


def authenticate_admin(db, login_id: str, password: str):
    admin = get_admin(db, login_id)
    if not admin:
        return False
    if not verify_password(password, admin.password):
        return False
    return admin


def create_access_token(user: User):
    hashed_token = get_password_hash(user.user_login_id + TOKEN_SALT)
    try:
        token_expiry = datetime.utcnow() + timedelta(
            minutes=common.global_variables.db_token_expiry_minutes[user.tenant_key])
    except KeyError:
        raise ConfigNotFoundException("Please configure access token expiry time for this tenant")
    return hashed_token, token_expiry


def get_user(db, username: str, tenant_key):
    return db.query(User).filter(func.lower(User.user_login_id) == username,
                                 User.tenant_key == tenant_key).filter(User.is_active == 1).first()


def get_admin(db, login_id: str):
    return db.query(Admin).filter(func.lower(Admin.login_id) == login_id).filter(Admin.is_active == 1).first()


def validate(db, logged_in_group_key, logged_in_roles, role_group_map_model=UserRolesUserGroupMap, role_model=UserRole):
    """
        Args:
            db: database
            logged_in_group_key: User Group Key
            logged_in_roles: array of application roles ["role1|role2","role3"]
            here, it will check either role 1 or role2 and role3
        Returns: If no proper roles found no permission exception raised
    """
    proceed = True
    group_key = "user_group_key"
    role_key = "user_role_key"
    role = "user_role"
    if role_model == AdminRole:
        group_key = "admin_group_key"
        role_key = "admin_role_key"
        role = "admin_role"

    roles = db.query(getattr(role_group_map_model, group_key), getattr(role_group_map_model, role_key),
                     getattr(role_model, role)).join(role_model, getattr(role_group_map_model, role_key)
                                                     == getattr(role_model, role_key)).filter(
        getattr(role_group_map_model, group_key) == logged_in_group_key).all()
    permissions = ",".join([getattr(_role, role) for _role in roles])
    for logged_in_role in logged_in_roles:
        def match_either(rl):
            for _role in str(rl).split("|"):
                if _role in permissions:
                    return True
            return False

        if not match_either(logged_in_role) and logged_in_role not in permissions:
            proceed = False
            break
    if not proceed:
        raise NO_PERMISSION_EXCEPTION
    return proceed
