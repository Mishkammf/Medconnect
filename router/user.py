
from typing import List

from fastapi import APIRouter, Depends, Header, Response, Body, Form
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from starlette import status

from apimodel.models import QueryModel
from apimodel.params import UserInfoSortingParam, ActiveStatus
from apimodel.request_models import UserInfoEdit, UserInfo, pagination_parameters, db_and_user, user_filters, Struct
from apimodel.response_models import APISuccess, UserInfoResponse, APIError, \
    Status
from common.application_roles import ALLOW_TO_DELETE_USERS, ALLOW_TO_UPDATE_USERS, \
    ALLOW_TO_GET_USERS, ALLOW_TO_GET_USER_DETAILS, ALLOW_TO_CHANGE_USER_PASSWORD
from common.database.db_session import get_db
from common.database.user import User
from common.db_exception_messages import user_integrity
from common.string_constants import db_instance, active_user, \
    shift_type_param, active_status_param, user_group_keys_param, user_group_key_string
from exceptions.custom_exceptions import ItemNotFoundException, DefaultUserDeleteException, DatabaseIntegrityException
from security import authentication_service
from security.authentication_service import get_password_hash, get_current_active_user, verify_password
from services.db_crud_operations import delete, create, update, retrieve, delete_multiple
from services.sql_helper import update_sort_and_pagination_in_query, get_search_filter

router = APIRouter()
primary_key_attribute = "user_key"


@router.post("", response_model=APISuccess, status_code=status.HTTP_201_CREATED)
def add_user(user_data: UserInfo, db: Session = Depends(get_db)):
    """
    Adds user to the system
    ***Return*** : The success status or exceptions of the operation
    """

    user_data.user_password = get_password_hash(
        user_data.user_password)
    try:
        user_key = create(db, User, user_data).user_key
        db.commit()
    except DatabaseIntegrityException:
        db.rollback()
        raise DatabaseIntegrityException(message=user_integrity)
    return APISuccess(id=user_key, message="User has been successfully added")


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
        temp_users = db.query(User).filter(User.user_key.in_(id_list)).all()
        member_ids = {}
        for temp_user in temp_users:
            if temp_user.default:
                id_list.remove(temp_user.user_key)
            member_ids[temp_user.user_key] = temp_user.member_id

        deleted_ids = delete_multiple(db, User, primary_key_attribute, id_list)

    if len(deleted_ids) == len(id_list):
        return APISuccess(message=f"Users with ids {id_list} have been successfully deleted")
    else:
        return APISuccess(status=Status.PARTIAL_SUCCESS.value,
                          message=f"Users with ids {deleted_ids} have been successfully deleted/disabled. "
                          f"Users with ids {(list(set(id_list) - set(deleted_ids)))} were not found")


@router.get("", response_model=List[UserInfoResponse])
def get_all_users(response: Response, text_search: str = None,
                  user_filter_params: dict = Depends(user_filters),
                  sorting_param: UserInfoSortingParam = Header(UserInfoSortingParam.CREATED_DATE),
                  pagination_values: dict = Depends(pagination_parameters),
                  db_and_user_param: dict = Depends(db_and_user)):
    """
    Fetch all the user details
    ***Return*** : All the users installed in the system
    """
    db, user = db_and_user_param[db_instance], db_and_user_param[active_user]
    authentication_service.validate(db, int(user[user_group_key_string]), [ALLOW_TO_GET_USERS])
    text_search = text_search.strip() if text_search is not None else ''
    query = update_sort_and_pagination_in_query(QueryModel(), sorting_param, pagination_values)
    filters = User.member_id.in_(query.member_ids)
    if user_filter_params[user_group_keys_param]:
        user_group_keys = [int(key) for key in user_filter_params[user_group_keys_param].split(" ")]
        filters = and_(filters, User.user_group_key.in_(user_group_keys))
    if user_filter_params[active_status_param] == ActiveStatus.ACTIVE:
        filters = and_(filters, User.is_active == 1)
    elif user_filter_params[active_status_param] == ActiveStatus.INACTIVE:
        filters = and_(filters, User.is_active == 0)
    if user_filter_params[shift_type_param]:
        shift_types = [int(shift_type) for shift_type in user_filter_params[shift_type_param].split(",")]
        filters = and_(filters, User.shift_type.in_(shift_types))
    return get_user_details(response, db, text_search.strip(), query, 0, filters)


def get_user_details(response, db, text_search, query, user_id, filters=True):
    """
    Method to download User information
    :param user_id: user id, optional when requesting all users
    :param query: queryModel object to use for setting filters, sorting and pagination
    :param text_search:
    :param db: Database session
    :param response: response object
    """
    search_filter = get_search_filter(text_search)

    filters = and_(filters, or_(User.user_key == user_id, user_id == 0),
                   or_(User.user_login_id.like(search_filter), User.first_name.like(search_filter),
                       User.last_name.like(search_filter),
                       User.member_id.like(search_filter)))

    select_fields = [User.created_datetime,
                     User.modified_datetime, User.first_name, User.last_name,  User.user_key,

                     User.email]
    db_model = User
    results, total_records = retrieve(db, db_model, query, filters, select_fields, row_number=True)
    response.headers["total-record-count"] = str(total_records)

    return [UserInfoResponse(
                             created_date=result.created_datetime,
                             modified_date=result.modified_datetime,
                             first_name=result.first_name,
                             last_name=result.last_name if result.last_name else "",
                             user_key=result.user_key,
                             email=result.email if result.email else "",)
            for result in results]


@router.get("/{user_id}", response_model=UserInfoResponse)
def get_user(response: Response, user_id: int, db: Session = Depends(get_db),
             user: {} = Depends(get_current_active_user)):
    """
        ***Return*** : Return User details for given user id\n
        params:\n
        user_id: Primary key of the user
    """
    authentication_service.validate(db, int(user[user_group_key_string]),
                                    [ALLOW_TO_GET_USERS + '|' + ALLOW_TO_GET_USER_DETAILS])
    details = get_user_details(response, db, None, None, user_id)
    if len(details) == 0:
        raise ItemNotFoundException(user_id, User)
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
def update_user(user_key: int, user_data: UserInfoEdit = Body(None), db: Session = Depends(get_db),
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
