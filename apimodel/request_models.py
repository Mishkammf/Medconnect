from datetime import datetime, date
from ipaddress import IPv4Address

from fastapi import Header, Query, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing_extensions import Literal

from apimodel.params import SortingOrder, ActiveStatus
from common.database.db_session import get_db
from common.string_constants import last_record_param, max_records_param, sorting_order_param, \
    start_date_param, end_date_param, time_zone_param, active_user, db_instance, shift_type_param, \
    active_status_param, user_group_keys_param, admin_group_keys_param, default_timezone
from security.authentication_service import get_current_active_user


class SignUpUserInfo(BaseModel):
    user_login_id: str
    user_password: str
    member_id: str
    first_name: str = None
    last_name: str = None


class UserInfo(SignUpUserInfo):
    tenant_key: str = None
    user_login_id: str = None
    user_password: str = None
    user_group_key: int = None
    default: int = 0
    is_active: bool = 0
    enable_login: bool = 0
    api_access_only: bool = 0
    enable_multiple_logins: bool = 0
    concurrent_logging_count: int = 1
    expire_token: bool = 0
    created_date: datetime = None
    modified_date: datetime = None
    email: str = None
    mobile_number: str = None


class HospitalInfo(BaseModel):
    hospital_key: int = None
    name: str
    total_gicu_beds_available: int = None
    total_gicu_beds_used: int = None
    total_sicu_beds_available: int = None
    total_sicu_beds_used: int = None


class HospitalInfoEdit(BaseModel):
    hospital_key: int = None
    name: str
    total_gicu_beds_available: int = None
    total_gicu_beds_used: int = None
    total_sicu_beds_available: int = None
    total_sicu_beds_used: int = None


class UserInfoEdit(BaseModel):
    tenant_key: int = None
    user_login_id: str = None
    user_password: str = None
    user_group_key: int = None
    email: str = None
    first_name: str = None
    last_name: str = None
    mobile_number: str = None
    api_access_only: bool = None
    expire_token: bool = None
    enable_multiple_logins: bool = None
    concurrent_logging_count: int = None
    is_active: bool = None
    member_id: str = None
    enable_login: bool = None
    title_key: int = None
    dob: date = None
    gender: Literal["M", "F"] = None
    project_key: int = None
    location_key: int = None
    shift_type: Literal[1, 2, 3] = None


class TransferRequestInfo(BaseModel):
    transfer_request_key: int
    doctor_id: int
    target_hospital_id: int
    patient_id: int = None
    created_datetime: datetime = None
    status: str = None


class TransferRequestInfoEdit(BaseModel):
    transfer_request_key: int
    doctor_id: int
    target_hospital_id: int
    patient_id: int = None
    created_datetime: datetime = None
    status: str = None


class AmbulanceRequestInfo(BaseModel):
    id: int
    ambulance_id: int
    doctor_id: int
    start_hospital_id: int
    end_hospital_id: int
    created_datetime: datetime = None
    status: str


class AmbulanceRequestInfoEdit(BaseModel):
    id: int
    ambulance_id: int
    doctor_id: int
    start_hospital_id: int
    end_hospital_id: int
    created_datetime: datetime = None
    status: str


class LoginInfo(BaseModel):
    ip_address: IPv4Address = None
    logged_in_out_datetime: datetime
    is_login: int = None
    device: int = None


class UserLoginInfo(LoginInfo):
    user_key: int


class Struct:
    pass


class UserTokenInfo(BaseModel):
    user_key: int
    token: str
    token_expiry: datetime = datetime.utcnow()
    created_datetime: datetime = datetime.utcnow()
    modified_datetime: datetime = datetime.utcnow()


async def pagination_parameters(last_record: int = Header(0), max_records: int = Header(20),
                                sorting_order: SortingOrder = Header(SortingOrder.ASCENDING)):
    return {last_record_param: last_record, max_records_param: max_records, sorting_order_param: sorting_order}


async def timestamp_filters(start_date: datetime = Query(...), end_date: datetime = Query(None),
                            time_zone: str = Header(default_timezone)):
    return {start_date_param: start_date, end_date_param: end_date, time_zone_param: time_zone}


async def db_and_user(db: Session = Depends(get_db)):
    return {db_instance: db, active_user: 345}


async def admin_filters(active_status: ActiveStatus = ActiveStatus.BOTH, admin_group_keys: str = Query([])):
    return {active_status_param: active_status, admin_group_keys_param: admin_group_keys}
