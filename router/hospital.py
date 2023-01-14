from typing import List

from fastapi import APIRouter, Depends, Header, Response, Body, Form, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from starlette import status

from apimodel.models import QueryModel
from apimodel.params import HospitalInfoSortingParam, ActiveStatus
from apimodel.request_models import HospitalInfoEdit, pagination_parameters, db_and_user, Struct, HospitalInfo
from apimodel.response_models import APISuccess, HospitalInfoResponse, APIError, \
    Status, BedTypeCountResponse
from common.application_roles import ALLOW_TO_DELETE_USERS, ALLOW_TO_UPDATE_USERS, \
    ALLOW_TO_GET_USERS, ALLOW_TO_GET_USER_DETAILS, ALLOW_TO_CHANGE_USER_PASSWORD
from common.database.db_session import get_db
from common.database.user import User
from common.database.hospital import Hospital
from common.db_exception_messages import user_integrity
from common.string_constants import db_instance, active_user, \
    shift_type_param, active_status_param, user_group_keys_param, user_group_key_string
from exceptions.custom_exceptions import ItemNotFoundException, DefaultUserDeleteException, DatabaseIntegrityException
from security import authentication_service
from security.authentication_service import get_password_hash, get_current_active_user, verify_password
from services.db_crud_operations import delete, create, update, retrieve, delete_multiple
from services.sql_helper import update_sort_and_pagination_in_query, get_search_filter

router = APIRouter()
primary_key_attribute = "hospital_key"


@router.post("", response_model=APISuccess, status_code=status.HTTP_201_CREATED)
def add_hospital(hospital_data: HospitalInfo, db: Session = Depends(get_db)):
    """
    Adds hospital to the system
    ***Return*** : The success status or exceptions to the operation
    """

    try:
        hospital_key = create(db, Hospital, hospital_data).hospital_key
        db.commit()
    except DatabaseIntegrityException:
        db.rollback()
        raise DatabaseIntegrityException(message=user_integrity)
    return APISuccess(id=hospital_key, message="Hospital has been successfully added")


@router.delete("/{user_id}", response_model=APISuccess)
def delete_user(user_id: int, db: Session = Depends(get_db), user: {} = Depends(get_current_active_user)):
    """
    Delete the user from the system
    ***Return*** : The success status or exceptions of the operation
    """
    authentication_service.validate(db, int(user[user_group_key_string]), [ALLOW_TO_DELETE_USERS])
    temp_user = db.query(User).filter(User.user_key == user_id).first()
    if temp_user and temp_user.default == 1:
        raise DefaultUserDeleteException()
    delete(db, User, primary_key_attribute, user_id)
    return APISuccess(message=f"User with id {user_id} has been successfully deleted")


@router.delete("", response_model=APISuccess)
def delete_users(user_keys: List[int] = Body(...), db: Session = Depends(get_db),
                 user: {} = Depends(get_current_active_user)):
    """
    Delete the specified users from the system
    ***Return*** : The success status or exceptions of the operation
    """
    authentication_service.validate(db, int(user[user_group_key_string]), [ALLOW_TO_DELETE_USERS])
    id_list = user_keys
    deleted_ids = []
    if id_list is not None:
        deleted_ids = delete_multiple(db, User, primary_key_attribute, id_list)

    if len(deleted_ids) == len(id_list):
        return APISuccess(message=f"Users with ids {id_list} have been successfully deleted")
    else:
        return APISuccess(status=Status.PARTIAL_SUCCESS.value,
                          message=f"Users with ids {deleted_ids} have been successfully deleted/disabled. "
                          f"Users with ids {(list(set(id_list) - set(deleted_ids)))} were not found")


@router.get("", response_model=List[HospitalInfoResponse])
def get_all_hospitals(response: Response, text_search: str = None,
                  sorting_param: HospitalInfoSortingParam = Header(HospitalInfoSortingParam.HOSPITAL_KEY),
                  pagination_values: dict = Depends(pagination_parameters),
                  db_and_user_param: dict = Depends(db_and_user)):
    """
    Fetch all the hospital details
    ***Return*** : All the users installed in the system
    """
    db, user = db_and_user_param[db_instance], db_and_user_param[active_user]
    # authentication_service.validate(db, int(user[user_group_key_string]), [ALLOW_TO_GET_USERS])
    text_search = text_search.strip() if text_search is not None else ''
    query = update_sort_and_pagination_in_query(QueryModel(), sorting_param, pagination_values)
    filters = True

    return get_hospital_details(response, db, text_search.strip(), query, 0, filters)


def get_hospital_details(response, db, text_search, query, hospital_key, filters=True):
    """
    Method to download User information
    :param hospital_key : user id, optional when requesting all users
    :param query: queryModel object to use for setting filters, sorting and pagination
    :param text_search:
    :param db: Database session
    :param response: response object
    """
    search_filter = get_search_filter(text_search)
    filters = and_(filters, or_(Hospital.hospital_key == hospital_key, hospital_key == 0),
                   or_(Hospital.name.like(search_filter)))
    select_fields = [Hospital.hospital_key, Hospital.name, Hospital.total_gicu_beds_used, Hospital.total_sicu_beds_used,
                     Hospital.total_gicu_beds_available, Hospital.total_sicu_beds_available]
    db_model = Hospital
    results, total_records = retrieve(db, db_model, query, filters, select_fields, row_number=True)
    response.headers["total-record-count"] = str(total_records)
    return [HospitalInfoResponse(
                             name=result.name,
                             hospital_key=result.hospital_key,
                             total_gicu_beds_used=result.total_gicu_beds_used,
                             total_sicu_beds_used=result.total_sicu_beds_used,
                             total_gicu_beds_available=result.total_gicu_beds_available,
                             total_sicu_beds_available=result.total_sicu_beds_available,)
            for result in results]


@router.get("/{hospital_key}", response_model=HospitalInfoResponse)
def get_hospital(response: Response, hospital_key: int, db: Session = Depends(get_db)):
    """
        ***Return*** : Return Hospital details for given hospital id\n
        params:\n
        hospital_key: Primary key of the hospital
    """

    details = get_hospital_details(response, db, None, None, hospital_key)
    if len(details) == 0:
        raise ItemNotFoundException(hospital_key, Hospital)
    response.status_code = 200
    return details[0]


@router.patch("/password", response_model=APISuccess)
def change_user_password(user_key: int = Form(...), old_password: str = Form(...), new_password: str = Form(...),
                         db: Session = Depends(get_db),
                         user: {} = Depends(get_current_active_user)):
    """
        ***Return*** : Return success status of operation
        params:\n
        user_id: Primary key of the user
    """
    authentication_service.validate(db, int(user[user_group_key_string]), [ALLOW_TO_CHANGE_USER_PASSWORD])
    current_password = retrieve(db, User, None, User.user_key == user_key, [User.user_password])[0]
    if not current_password:
        raise ItemNotFoundException(db_id=user_key)
    current_password = current_password[0][0]
    if not verify_password(old_password, current_password):
        return APIError(message="Incorrect current password")
    user_data = Struct()
    user_data.user_password = get_password_hash(new_password)
    update(db, User, user_data, primary_key_attribute, user_key)

    return APISuccess(message=f"Password of user with id {user_key} has been successfully updated")


@router.patch("/{user_key}", response_model=APISuccess)
def update_user(user_key: int, user_data: HospitalInfoEdit = Body(None), db: Session = Depends(get_db),
                user: {} = Depends(get_current_active_user)):
    """
    Update the user info
    ***Return*** : The success status or exceptions of the operation
    """
    authentication_service.validate(db, int(user[user_group_key_string]), [ALLOW_TO_UPDATE_USERS])
    user_data.user_password = get_password_hash(
        user_data.user_password) if user_data.user_password else None
    try:
        current_data = retrieve(db, User, None, User.user_key == user_key, [User])[0]
        if not current_data:
            raise ItemNotFoundException()
        update(db, User, user_data, primary_key_attribute, user_key)
    except DatabaseIntegrityException:
        db.rollback()
        raise DatabaseIntegrityException(message=user_integrity)
    return APISuccess(message=f"User with id {user_key} has been successfully updated")

@router.get("/counts/{bed_type}", response_model=List[BedTypeCountResponse])
def get_hospital_bed_count(response: Response, bed_type: str, db: Session = Depends(get_db)):
    """
        ***Return*** : Return Count of beds of type bed_type
        bed_type: Bed type to search
    """

    select_fields = [Hospital.hospital_key, Hospital.name]
    if bed_type == "gicu":
        select_fields.extend([Hospital.total_gicu_beds_available.label("available"),
                              Hospital.total_gicu_beds_used.label("used")])

    if bed_type == "sicu":
        select_fields.extend([Hospital.total_sicu_beds_available.label("available"),
                              Hospital.total_sicu_beds_used.label("used")])

    db_model = Hospital
    results, total_records = retrieve(db, db_model, None, True, select_fields, row_number=True)
    response.headers["total-record-count"] = str(total_records)

    return [BedTypeCountResponse(
                             hospital_name=result.name,
                             hospital_key=result.hospital_key,
                             bed_count=result.available-result.used)
            for result in results]

