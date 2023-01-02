

from common.string_constants import last_record_param, max_records_param, sorting_order_param, time_zone_param, \
    start_date_param, end_date_param
from services.results_creator_helper import get_tz_adjustment
from validation.datetime_validation import validate_start_end_relativity


def get_search_filter(text_search):
    if not text_search:
        text_search = ""
    search_filter = "%{}%".format(text_search)
    return search_filter


def update_sort_and_pagination_in_query(query, sorting_param, pagination_parameters):
    sorting_param = sorting_param.value if sorting_param is not None else sorting_param
    query.sort_param = sorting_param
    if pagination_parameters:
        sorting_order = pagination_parameters[sorting_order_param].value if pagination_parameters[sorting_order_param] \
                                                                            is not None else pagination_parameters[
            sorting_order_param]
        query.sort_order = sorting_order
        query.offset = pagination_parameters[last_record_param]
        query.limit = pagination_parameters[max_records_param]
    return query



def update_filters_in_query(query, camera_ids, location_key, filter_values,
                            tenant_time_zone, tenant_key):
    time_zone = filter_values[time_zone_param]
    start_timestamp = filter_values[start_date_param]
    end_timestamp = filter_values[end_date_param]
    validate_start_end_relativity(start_timestamp, end_timestamp)
    query.camera_ids = camera_ids
    query.tenant_key = tenant_key
    query.time_zone = time_zone
    query.start_date = start_timestamp
    query.end_date = end_timestamp

    return query


def get_filter_query(db, member_ids, project_keys, demography_filters, title_keys,
                     tenant_key, self_data=None):
    pass

def get_time_filter(query, db_model):
    """
    Creates time filter to use for SQL filter based on input start/end timestamps
    :param query: QueryModel instance
    :param db_model: Database entity
    :return: SQL Alchemy time filter
    """
    if query.start_date and query.end_date:
        time_filter = db_model.timestamp.between(query.start_date - get_tz_adjustment(query.time_zone),
                                                 query.end_date - get_tz_adjustment(query.time_zone))
    elif query.start_date:
        time_filter = db_model.timestamp > query.start_date - get_tz_adjustment(query.time_zone)
    elif query.end_date:
        time_filter = db_model.timestamp < query.end_date - get_tz_adjustment(query.time_zone)
    else:
        time_filter = True
    return time_filter
