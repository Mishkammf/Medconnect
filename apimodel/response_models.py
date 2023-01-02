import datetime
from enum import Enum
from typing import List, TypeVar

from pydantic import BaseModel

dataType = TypeVar("dataType")


class Status(Enum):
    SUCCESS = "successful",
    FAIL = "fail"
    PARTIAL_SUCCESS = "partially successful"


class APIError(BaseModel):
    status: Status = Status.FAIL.value
    type: str = None
    message: str


class APISuccess(BaseModel):
    status: Status = Status.SUCCESS.value
    message: str
    id: int = None
    camera_id: str = None
    id_list: List[int] = None


class DBObjectResponse(BaseModel):
    created_date: datetime.datetime = None
    modified_date: datetime.datetime = None


class UserInfoResponse(DBObjectResponse):
    user_key: int = None
    first_name: str = None
    last_name: str = None
    email: str = None














