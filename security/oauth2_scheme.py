
from fastapi.security import OAuth2PasswordBearer

from init import COMMON_API_PREFIX

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{COMMON_API_PREFIX}/token")
