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


class HospitalInfoResponse(DBObjectResponse):
    hospital_key: int
    name: str
    total_gicu_beds_available: int = None
    total_gicu_beds_used: int = None
    total_sicu_beds_available: int = None
    total_sicu_beds_used: int = None


class TransferRequestInfoResponse(DBObjectResponse):
    transfer_request_key: int
    doctor_id: int
    target_hospital_id: int
    patient_id: int
    status: str

class BedTypeCountResponse(BaseModel):
    hospital_name: str = None
    hospital_key: int = None
    bed_count: int = None

class AmbulanceRequestInfoResponse(DBObjectResponse):
    id: int
    ambulance_id: int
    doctor_id: int
    start_hospital_id: int
    end_hospital_id: int
    created_datetime: datetime.datetime = None
    status: str


