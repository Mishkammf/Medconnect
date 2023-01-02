import datetime

from apimodel.models import QueryModel
from apimodel.params import UserTokenSortingParam, SortingOrder
from apimodel.request_models import UserTokenInfo, UserLoginInfo
from common.database.user_login_history import UserLoginHistory
from common.database.user_token import UserToken
from common.string_constants import db_user_key, db_login_history_time, db_login_history_is_login, \
    db_token_id, db_user_token, db_token_expiry
from common.string_constants import last_record_param, max_records_param, sorting_order_param
from exceptions.custom_exceptions import ItemsNotFoundException
from security.authentication_service import create_access_token
from services.db_crud_operations import create, retrieve, delete_multiple
from services.sql_helper import update_sort_and_pagination_in_query


def handle_tokens_at_login(db, user, device):
    if not user.enable_multiple_logins:
        try:
            item_data = {
                db_user_key: user.user_key,
                db_login_history_time: datetime.datetime.utcnow(),
                db_login_history_is_login: 3
            }
            item_data = UserLoginInfo(**item_data)
            create(db, UserLoginHistory, item_data)
            delete_multiple(db, UserToken, db_user_key, [user.user_key], None)
        except ItemsNotFoundException as e:
            print("No Active User Tokens : " + str(e))
    else:
        filters = UserToken.user_key == user.user_key
        pagination_values = {last_record_param: None, max_records_param: None,
                             sorting_order_param: SortingOrder.ASCENDING}
        query = update_sort_and_pagination_in_query(QueryModel(), UserTokenSortingParam.CREATED_DATE_TIME,
                                                    pagination_values)
        tokens, count = retrieve(db, UserToken, query, filters, [UserToken])
        if user.concurrent_logging_count <= count:
            delete_multiple(db, UserToken, db_token_id, [tokens[0].id], None)
            item_data = {
                db_user_key: tokens[0].user_key,
                db_login_history_time: datetime.datetime.utcnow(),
                db_login_history_is_login: 3
            }
            item_data = UserLoginInfo(**item_data)
            create(db, UserLoginHistory, item_data)

    hashed_token, token_expiry = create_access_token(user)
    token_obj = UserTokenInfo(**{db_user_token: hashed_token, db_token_expiry: token_expiry, db_user_key: user.user_key})
    create(db, UserToken, token_obj)
    create(db, UserLoginHistory)
    return hashed_token

