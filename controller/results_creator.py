
from datetime import datetime, timedelta

import common.global_variables
from apimodel.models import QueryModel, AttendanceData, InOutData
from apimodel.params import AttendanceStatus
from apimodel.response_models import CameraActivityResponse, MemberActivityResponse, MemberAttendanceResponse, \
    AttendanceSummaryResponse, VehicleAttendanceResponse, VehicleActivityResponse, TimeString, DailyAttendanceResponse, \
    Task, WorkProject, WorkDayDurationStatsResponse
from common.config_manager import get_config
from common.database.stranger import Stranger
from common.string_constants import es_timestamp, es_camera_id, es_person_id, es_image_path, NO_DATA, es_person_keyword, \
    es_plate_number_keyword, es_number_plate, es_province, DURATION_ICON_DIR, indeterminate_work_duration, es_sign_in, \
    default_work_duration_key, zero_hours, es_record_type, es_system_record_type, no_out_note, stranger_id_prefix, \
    start_date_param, end_date_param, time_zone_param
from controller import es_retriever
from services.request_validation import get_tenant_data
from services.results_creator_helper import get_member_name_scores, get_location_scores, get_member_id_scores, \
    get_formatted_date, get_vehicle_owner_scores, get_is_sign_in, fill_day_and_hour
from services.sql_helper import update_filters_in_query

static_url = get_config('backend_api.static_url_path')


def get_sorted_and_paginated_result(results, query: QueryModel):
    """
    Sorts records based on given parameters and returns paginated result.
    Args:
        results (list): list of records
        results (list): list of records
        query (QueryModel): queryModel object to use for setting filters, sorting and pagination

    Returns:
        List of sorted records
    """
    if not query.limit:
        query.limit = len(results)
    if query.sort_order and query.sort_param:
        reverse = True if query.sort_order == "desc" else False
        if query.sort_param == "member_id":
            member_ids_in_results = [x.member_id for x in results]
            results.sort(key=lambda x: get_member_id_scores(query.tenant_key, member_ids_in_results)[x.member_id],
                         reverse=reverse)
            return results[query.offset:query.offset + query.limit]
        else:
            results.sort(key=lambda x: (getattr(x, query.sort_param) is None, getattr(x, query.sort_param)),
                         reverse=reverse)
            return results[query.offset:query.offset + query.limit]
    else:
        return results


def get_member_activity_responses(query, records, stranger):
    results = []

    for record in records:
        key = record[es_person_id]
        if es_sign_in not in record:
            record[es_sign_in] = None
        is_sign_in = get_is_sign_in(query.tenant_key,
                                    InOutData(camera_id=record[es_camera_id], sign_in_status=record[es_sign_in]))
        if is_sign_in == 2:
            is_sign_in = None
        location = common.global_variables.get_id_from_key(
            common.global_variables.db_camera_locations[query.tenant_key],
            record[es_camera_id].lower())
        timestamp = get_formatted_date(record[es_timestamp], query.time_zone)
        if stranger:
            results.append(
                MemberActivityResponse(icon_path=f'{static_url}/strangers/{query.tenant_key}/{record[es_image_path]}',
                                       first_name=NO_DATA, stranger_key=int(key.strip(stranger_id_prefix)),
                                       last_name=NO_DATA, member_id=key, location=location, timestamp=timestamp))
        else:
            icon_path = f'{static_url}/icon_pics/{query.tenant_key}/{key}.jpg'
            if key in common.global_variables.db_member_names[query.tenant_key]:
                results.append(MemberActivityResponse(icon_path=icon_path, member_id=key,
                                                      first_name=common.global_variables.get_id_from_key(
                                                          common.global_variables.db_member_names[query.tenant_key],
                                                          key)[0],
                                                      last_name=common.global_variables.get_id_from_key(
                                                          common.global_variables.db_member_names[query.tenant_key],
                                                          key)[1],
                                                      is_sign_in=is_sign_in, es_doc_id=record['es_doc_id'],
                                                      location=location, timestamp=timestamp,
                                                      record_type=record[es_record_type]))

    return results


def get_vehicle_activity_responses(query, records, unregistered_vehicle):
    results = []
    for record in records:
        key = record[es_number_plate]
        location = common.global_variables.get_id_from_key(
            common.global_variables.db_camera_locations[query.tenant_key],
            record[es_camera_id].lower())
        timestamp = get_formatted_date(record[es_timestamp], query.time_zone)
        if unregistered_vehicle:
            if record[es_province] == "":
                record[es_province] = NO_DATA
            results.append(
                VehicleActivityResponse(owner_name=NO_DATA, owner_company=NO_DATA,
                                        plate_number=key,
                                        province=record[es_province],
                                        location=location, timestamp=timestamp))
        else:
            vehicle = common.global_variables.get_id_from_key(
                common.global_variables.db_vehicle_data[query.tenant_key], key)

            results.append(VehicleActivityResponse(owner_name=vehicle[1], owner_company=vehicle[2],
                                                   plate_number=key,
                                                   province=vehicle[0],
                                                   location=location, timestamp=timestamp))

    return results


def get_member_activity(query, is_last_seen, es_index, stranger):
    """
    Fetches records from ES with match the given filter, sorting and pagination values.
    Args:
        query (QueryModel): queryModel object to use for setting filters, sorting and pagination
        es_index (String): ES index to use for querying
        is_last_seen (boolean): whether to fetch last-seen data
        stranger (Boolean): if stranger

    Returns:
        List of records
    """
    sort_param = query.sort_param
    member_ids = query.member_ids
    if not is_last_seen:
        scores = None
        if sort_param == "first_name" or sort_param == "last_name":
            scores = get_member_name_scores(sort_param, member_ids,
                                            common.global_variables.db_users[query.tenant_key])
        elif sort_param == "location":
            scores = get_location_scores(common.global_variables.db_cameras[query.tenant_key])
        elif sort_param == "member_id":
            scores = get_member_id_scores(query.tenant_key, member_ids)
        records, total_records = es_retriever.get_records(query, es_index, scores)
    else:
        records, total_records = es_retriever.get_last_seen(query, es_index, es_person_keyword)
    results = get_member_activity_responses(query, records, stranger)
    if is_last_seen:
        results = get_sorted_and_paginated_result(results, query)
    return results, total_records


def get_vehicle_activity(query, is_last_seen, es_index, stranger):
    """
    Fetches vehicle records from ES with match the given filter, sorting and pagination values.
    Args:
        query (QueryModel): queryModel object to use for setting filters, sorting and pagination
        es_index (String): ES index to use for querying
        is_last_seen (boolean): whether to fetch last-seen data
        stranger (Boolean): if stranger

    Returns:
        List of records
    """
    sort_param = query.sort_param
    plate_numbers = query.plate_numbers

    if not is_last_seen:
        scores = None
        if sort_param == "owner_name" or sort_param == "owner_company":
            scores = get_vehicle_owner_scores(sort_param, plate_numbers,
                                              common.global_variables.db_vehicle_data[query.tenant_key])
        elif sort_param == "location":
            scores = get_location_scores(common.global_variables.db_cameras[query.tenant_key])
        records, total_records = es_retriever.get_records(query, es_index, scores, not stranger)

    else:
        records, total_records = es_retriever.get_last_seen(query, es_index, es_plate_number_keyword)
    results = get_vehicle_activity_responses(query, records, stranger)

    if is_last_seen:
        results = get_sorted_and_paginated_result(results, query)
    return results, total_records


def get_livestream(query, sort, member_logs_es_index, stranger_logs_es_index, stranger_image_paths):
    """
    Fetches most recent records in the given camera
    Args:
        query (QueryModel): queryModel object to use for setting filters, sorting and pagination
        sort (boolean): if sorting is required
        member_logs_es_index (string): member logs index
        stranger_logs_es_index (string): stranger logs index
        stranger_image_paths (dict)

    Returns:
        List of records
    """
    response = []
    live_members, live_strangers = es_retriever.get_live_data(query, member_logs_es_index,
                                                              stranger_logs_es_index)
    query.end_date = datetime.date(datetime.now())
    query.start_date = query.end_date - timedelta(days=7)

    regular_strangers = es_retriever.get_strangers(query, True, stranger_logs_es_index, get_all=True)
    regular_strangers = [regular_stranger.stranger_id for regular_stranger in regular_strangers]
    for record in live_members:
        member_id = record[es_person_id]
        timestamp = get_formatted_date(record[es_timestamp], query.time_zone)
        try:
            first_name = \
                common.global_variables.get_id_from_key(common.global_variables.db_member_names[query.tenant_key],
                                                        member_id)[0]
            last_name = \
                common.global_variables.get_id_from_key(common.global_variables.db_member_names[query.tenant_key],
                                                        member_id)[1]
        except KeyError:
            first_name, last_name = NO_DATA, NO_DATA
        try:
            db_id = common.global_variables.get_id_from_key(common.global_variables.db_member_ids[query.tenant_key],
                                                            member_id)
        except KeyError:
            db_id = 0
        try:
            location = common.global_variables.get_id_from_key(
                common.global_variables.db_camera_locations[query.tenant_key],
                record[es_camera_id].lower())
        except KeyError:
            location = NO_DATA
        response.append(
            CameraActivityResponse(id=db_id, first_name=first_name,
                                   last_name=last_name,
                                   member_id=member_id,
                                   stored_image_path=f'{static_url}/icon_pics/{query.tenant_key}/{member_id}.jpg',
                                   captured_image_path=f'{static_url}/live/{query.tenant_key}/{member_id}.jpg',
                                   timestamp=timestamp, type=1, location=location))

    for record in live_strangers:

        timestamp = get_formatted_date(record[es_timestamp], query.time_zone)
        stranger_id = record[es_person_id]
        if stranger_id in regular_strangers:
            record_type = 2
        else:
            record_type = 3
        try:
            stored_image_path = stranger_image_paths[stranger_id]
        except KeyError:
            stored_image_path = NO_DATA
        response.append(
            CameraActivityResponse(member_id=stranger_id, stored_image_path=stored_image_path,
                                   captured_image_path=
                                   f'{static_url}/strangers/{query.tenant_key}/{record[es_image_path]}',
                                   timestamp=timestamp, type=record_type,
                                   location=common.global_variables.db_camera_locations[query.tenant_key][
                                       record[es_camera_id].lower()]))
    if sort:
        query.sort_param = 'timestamp'
        query.sort_order = "desc"
        query.limit = len(response)
        query.offset = 0
        return get_sorted_and_paginated_result(response, query)
    else:
        return response


def adjust_hours_minutes(total_minutes):
    time_string = TimeString()
    time_string.hours = total_minutes // 60
    time_string.minutes = time_string.minutes % 60
    return time_string


def get_summary_values(result, total_present_days, total_in_time_seconds,
                       total_out_time_seconds, total_out_record_count, total_office_minutes, total_working_minutes):
    total_present_days += result.present_days
    in_time = result.in_time.time()
    total_in_time_seconds += in_time.hour * 3600 + in_time.minute * 60 + in_time.second
    if result.out_time:
        out_time = result.out_time.time()
        total_out_time_seconds += out_time.hour * 3600 + out_time.minute * 60 + out_time.second
        total_out_record_count += 1
    total_office_minutes += int(result.hours.split(":")[0]) * 60 + int(result.hours.split(":")[1])
    total_working_minutes += int(result.working_hours.split(":")[0]) * 60 + int(
        result.working_hours.split(":")[1])
    return total_present_days, total_in_time_seconds, total_out_time_seconds, \
           total_out_record_count, total_office_minutes, total_working_minutes


def get_attendance_summary(query, results, member_count):
    """
    Creates attendance summary response
    Args:
        query: query
        results: attendance results for given date
        member_count: total member count

    Returns:
        Attendance summary response
    """
    total_record_count = len(results)
    present_member_count = len(set([result.member_id for result in results]))
    avg_in_time = zero_hours
    avg_out_time = zero_hours
    avg_office_hours = zero_hours
    avg_working_hours = zero_hours
    total_office_hours = zero_hours
    total_working_hours = zero_hours
    total_present_days = 0
    avg_present_days = 0
    avg_members_per_day = 0
    total_out_time_seconds = 0
    total_out_record_count = 0
    if total_record_count:
        total_present_days = results[0].present_days
        in_time = results[0].in_time.time()
        total_in_time_seconds = in_time.hour * 3600 + in_time.minute * 60 + in_time.second
        if results[0].out_time:
            out_time = results[0].out_time.time()
            total_out_time_seconds += out_time.hour * 3600 + out_time.minute * 60 + out_time.second
            total_out_record_count += 1
        total_office_minutes = int(results[0].hours.split(":")[0]) * 60 + int(
            results[0].hours.split(":")[1])
        total_working_minutes = int(results[0].working_hours.split(":")[0]) * 60 + int(
            results[0].working_hours.split(":")[1])
        for result in results[1:]:
            total_present_days, total_in_time_seconds, total_out_time_seconds, \
            total_out_record_count, total_office_minutes, total_working_minutes = \
                get_summary_values(result, total_present_days,
                                   total_in_time_seconds, total_out_time_seconds, total_out_record_count,
                                   total_office_minutes, total_working_minutes)

        total_office_hours = f'{str(int(total_office_minutes // 60)).zfill(2)}' \
            f':{str(total_office_minutes % 60).zfill(2)}'
        total_working_hours = f'{str(int(total_working_minutes // 60)).zfill(2)}' \
            f':{str(total_working_minutes % 60).zfill(2)}'
        total_office_minutes = total_office_minutes / present_member_count
        total_working_minutes = total_working_minutes / present_member_count
        avg_office_hours = f'{str(int(total_office_minutes // 60)).zfill(2)}' \
            f':{str(int(total_office_minutes % 60)).zfill(2)}'
        avg_working_hours = f'{str(int(total_working_minutes // 60)).zfill(2)}' \
            f':{str(int(total_working_minutes % 60)).zfill(2)}' \
            f'' \
            f''
        avg_in_time_seconds = total_in_time_seconds / total_record_count
        avg_in_time = f'{str(int(avg_in_time_seconds // 3600)).zfill(2)}' \
            f':{str(int((avg_in_time_seconds % 3600) // 60)).zfill(2)}'
        if total_out_record_count:
            avg_out_time_seconds = total_out_time_seconds / total_out_record_count
            avg_out_time = f'{str(int(avg_out_time_seconds // 3600)).zfill(2)}' \
                f':{str(int((avg_out_time_seconds % 3600) // 60)).zfill(2)}'
        day_count = (query.end_date - query.start_date).days
        if day_count < 1:
            day_count = 1
        avg_present_days = round(total_present_days / member_count, 2)
        avg_members_per_day = round(total_present_days / day_count, 2)
    return AttendanceSummaryResponse(total_member_count=member_count,
                                     present_member_count=present_member_count,
                                     absent_member_count=member_count - present_member_count,
                                     avg_in_time=avg_in_time,
                                     avg_out_time=avg_out_time,
                                     total_working_hours=total_working_hours,
                                     total_office_hours=total_office_hours,
                                     avg_office_hours=avg_office_hours,
                                     avg_working_hours=avg_working_hours,
                                     total_present_days=total_present_days,
                                     avg_present_days=avg_present_days,
                                     avg_members_per_day=avg_members_per_day)


def get_in_out_times(in_and_out, time_zone):
    in_time, out_time, all_in_and_outs = None, None, []
    in_index, out_index = 0, -1
    first_is_system = False
    in_camera, out_camera, in_geo_info, out_geo_info, in_geo_fence, out_geo_fence = None, None, None, None, None, None
    for values in in_and_out:
        if values.sign_in_status:
            if values.record_type == es_system_record_type:
                first_is_system = True
            in_time = get_formatted_date(values.timestamp, time_zone)
            in_index = in_and_out.index(values)
            in_camera = values.camera_id
            in_geo_info = values.geo_stamp
            in_geo_fence = values.geo_fence
            break
    out_records = in_and_out[in_index + 1:][::-1]
    if first_is_system:
        out_records = in_and_out[in_index + 1:]
    for values in out_records:
        if not values.sign_in_status:
            out_time = get_formatted_date(values.timestamp, time_zone)
            out_camera = values.camera_id
            out_index = in_and_out.index(values)
            all_in_and_outs = in_and_out[in_index:out_index + 1]
            out_geo_info = values.geo_stamp
            out_geo_fence = values.geo_fence
            break
    last_record_time = get_formatted_date(in_and_out[-1].timestamp, time_zone)
    return AttendanceData(times=[in_time, out_time], cameras=[in_camera, out_camera],
                          geo_infos=[in_geo_info, out_geo_info],
                          geo_fences=[in_geo_fence, out_geo_fence]), in_index, last_record_time, all_in_and_outs


def get_work_day_duration(tenant_key, working_minutes):
    if tenant_key in common.global_variables.db_work_day_durations:
        for work_day in [duration for duration in common.global_variables.db_work_day_durations[tenant_key]]:
            if work_day.minutes_lower <= working_minutes <= work_day.minutes_upper:
                return work_day.description
    return indeterminate_work_duration


def get_working_hours(in_and_out, time_zone, continuous_attendance, tenant_key):
    """
    Calculates working hours based on in and out captures
    Args:
        in_and_out: in and out captures of member
        time_zone: time zone of client
        continuous_attendance: whether to calculate based on shifts
        tenant_key: tenant_key of client

    Returns:

    """

    start_time = datetime(2000, 1, 1, minute=0, hour=0)
    working_hours = datetime(2000, 1, 1, minute=0, hour=0).timestamp()
    member_is_working = False
    in_time = None
    in_date = None
    for record in in_and_out:
        record_datetime = get_formatted_date(record.timestamp, time_zone)
        if not continuous_attendance and in_date != record_datetime.date():
            member_is_working = False

        if get_is_sign_in(tenant_key, record) == 1 and not member_is_working:
            member_is_working = True
            in_time = record_datetime.timestamp()
            in_date = record_datetime.date()
        elif get_is_sign_in(tenant_key, record) == 0 and member_is_working:
            member_is_working = False
            out_time = record_datetime.timestamp()
            working_hours = working_hours + out_time - in_time

    difference = (datetime.fromtimestamp(working_hours) - start_time)
    hours = difference.days * 24 + difference.seconds // 3600
    minutes = (difference.seconds // 60) % 60
    work_day_duration = get_work_day_duration(tenant_key, hours * 60 + minutes)
    working_hours = str(hours).zfill(2) + ":" + str(minutes).zfill(2)
    return str(working_hours), work_day_duration


def update_attendance_results(attendance_results, time_values, next_day_time_values, query, continuous_attendance,
                              member_id, system_in_duration):
    result = extract_attendance_datetime(time_values, next_day_time_values, query.time_zone,
                                         continuous_attendance, query.tenant_key, system_in_duration)
    if result:
        result.member_id = member_id
        attendance_results.append(result)

    return attendance_results


def get_es_attendance_records(query, es_index, aggregator):
    continuous_attendance = False
    if query.tenant_key in common.global_variables.db_continuous_attendance_tenants:
        continuous_attendance = common.global_variables.db_continuous_attendance_tenants[query.tenant_key]

    if continuous_attendance:
        query.omit_sys_records = False
    return es_retriever.get_in_out_records_from_es(query, es_index, aggregator), continuous_attendance


def get_attendance_results(query: QueryModel, es_index, aggregator):
    """
    Calculates member attendance for given date while applying filters, sorting and pagination
    List of attendance data for given date
    Args:
        :param es_index: ES index to use for querying
        :param query: queryModel object to use for setting filters, sorting and pagination
        :param aggregator:
    Returns:
    """
    attendance_records, continuous_attendance = get_es_attendance_records(query, es_index, aggregator)

    attendance_results = []
    for date, member_attendance in attendance_records.items():
        next_day = date + timedelta(days=1)
        for member_id, time_values in member_attendance.items():
            next_day_time_values = None
            if next_day in attendance_records and continuous_attendance and member_id in attendance_records[next_day]:
                next_day_time_values = attendance_records[next_day][member_id]

            if member_id in common.global_variables.db_member_names[query.tenant_key]:

                attendance_results = update_attendance_results(attendance_results, time_values, next_day_time_values,
                                                               query, continuous_attendance, member_id, False)
                if time_values[0].record_type == es_system_record_type and get_formatted_date(time_values[0].timestamp,
                                                                                              query.time_zone).hour == 0:
                    # first record is a system record
                    time_values.pop(0)
                    attendance_results = update_attendance_results(attendance_results, time_values,
                                                                   next_day_time_values,
                                                                   query, continuous_attendance, member_id, True)

    return attendance_results


def get_duration_key(work_day_duration, query):
    duration_key = -1
    if work_day_duration and work_day_duration != indeterminate_work_duration and query.tenant_key in \
            common.global_variables.db_work_day_durations.keys():
        duration_key = \
            [duration.work_day_duration_key for duration in
             common.global_variables.db_work_day_durations[query.tenant_key] if
             duration.description == work_day_duration][0]
    return duration_key


def create_member_attendance_response(results, query: QueryModel, attendance_status_filter=AttendanceStatus.BOTH,
                                      work_day_durations_filter=None):
    """
    Calculates member attendance for given date while applying filters, sorting and pagination
    Args:
        es_index (String): ES index to use for querying
        query (QueryModel): queryModel object to use for setting filters, sorting and pagination
    Returns:
        List of attendance data for given date
        :param query:
        :param results:
        :param work_day_durations_filter:
        :param attendance_status_filter:
    """
    attendance = []
    for result in results:
        if not result:
            continue
        result.in_date = result.in_time.date()
        if result.out_time:
            result.out_date = result.out_time.date()

        in_location, out_location, in_device, out_device = get_in_out_devices(query.tenant_key, result.in_camera,
                                                                              result.out_camera)

        if attendance_status_filter != AttendanceStatus.BOTH and result.attendance_status != int(
                attendance_status_filter):
            continue

        duration_key = get_duration_key(result.work_day_duration, query)

        if work_day_durations_filter and duration_key not in [int(key) for key in work_day_durations_filter.split(",")]:
            continue
        duration_icon = f"{static_url}{DURATION_ICON_DIR}{query.tenant_key}/{duration_key}.jpg"
        if result.member_id in common.global_variables.db_member_names[query.tenant_key]:
            record = MemberAttendanceResponse(member_id=result.member_id,
                                              first_name=common.global_variables.get_id_from_key(
                                                  common.global_variables.db_member_names[query.tenant_key],
                                                  result.member_id)[
                                                  0],
                                              last_name=common.global_variables.get_id_from_key(
                                                  common.global_variables.db_member_names[query.tenant_key],
                                                  result.member_id)[
                                                  1],
                                              in_time=result.in_time, out_time=result.out_time, hours=result.duration,
                                              date=result.in_date, in_date=result.in_date, out_date=result.out_date,
                                              attendance_status=result.attendance_status,
                                              present_days=result.present_days,
                                              duration_icon=duration_icon,
                                              in_device=in_device,
                                              out_device=out_device,
                                              work_day_duration=result.work_day_duration,
                                              working_hours=result.working_hours,
                                              in_location=in_location, out_location=out_location,
                                              icon=f'{static_url}/icon_pics/{query.tenant_key}/{result.member_id}.jpg',
                                              in_geo_info=result.in_geo_info, out_geo_info=result.out_geo_info,
                                              in_geo_fence=result.in_geo_fence, out_geo_fence=result.out_geo_fence)
            attendance.append(record)
    return attendance
def get_total_working_hours(results):
    total_hours = {}

    for result in results:
        if result.working_hours is None:
            continue
        member_id = result.member_id
        if member_id not in total_hours:
            total_hours[member_id] = int(result.working_hours.split(":")[0]) * 60 + int(
            result.working_hours.split(":")[1])
        else:
            total_hours[member_id] += int(result.working_hours.split(":")[0]) * 60 + int(
                result.working_hours.split(":")[1])
    for result in results:
        if result.total_working_hours:
            continue
        if result.member_id in total_hours:
            result.total_working_hours = f'{str(total_hours[result.member_id] // 60).zfill(2)}:{str(total_hours[result.member_id] % 60).zfill(2)}'
        else:
            result.total_working_hours = zero_hours
    return results


def add_absent_member_records(results, query):
    all_dates = fill_day_and_hour(query, "day")
    absent_records = []
    for request_date in all_dates:
        request_date = request_date.date()
        present_members = [result.member_id for result in results if result.date == request_date]
        absent_members = [member for member in query.member_ids if member not in present_members]
        for member_id in absent_members:
            first_name, last_name = None, None
            if member_id in common.global_variables.db_member_names[query.tenant_key]:
                first_name = common.global_variables.get_id_from_key(
                    common.global_variables.db_member_names[query.tenant_key],
                    member_id)[0]

                last_name = common.global_variables.get_id_from_key(
                    common.global_variables.db_member_names[query.tenant_key],
                    member_id)[1]

            record = MemberAttendanceResponse(member_id=member_id, first_name=first_name, last_name=last_name,
                                              date=request_date, if_present_record=False, in_date=request_date,
                                              hours="-",
                                              in_device="-",
                                              in_location="-",
                                              out_device="-",
                                              out_location="-",
                                              work_day_duration="-",
                                              icon=f'{static_url}/icon_pics/{query.tenant_key}/{member_id}.jpg')
            absent_records.append(record)
    return absent_records


def get_work_day_duration_stats(tenant_key, results):
    """
    Creates attendance summary response
    Args:
        tenant_key: tenant_key of client
        results: attendance results for given date

    Returns:
        Attendance summary response
    """
    all_work_day_durations = {}
    try:
        durations = common.global_variables.db_work_day_durations[tenant_key]
    except KeyError:
        durations = []
    for work_day_duration in durations:
        all_work_day_durations[work_day_duration.description] = 0
    work_day_duration_response = []
    all_work_day_durations[indeterminate_work_duration] = 0
    all_work_day_durations[no_out_note] = 0
    for result in results:
        minutes = int(result.working_hours.split(":")[0]) * 60 + int(
            result.working_hours.split(":")[1])
        if not minutes:
            all_work_day_durations[no_out_note] += 1
        else:
            description = get_work_day_duration(tenant_key, minutes)
            all_work_day_durations[description] += 1
    if all_work_day_durations[indeterminate_work_duration] == 0:
        all_work_day_durations.pop(indeterminate_work_duration)
    for description, member_count in all_work_day_durations.items():
        duration_key = default_work_duration_key
        hours_lower = None
        hours_upper = None
        if description == no_out_note:
            duration_key = -1

        elif description != indeterminate_work_duration:
            duration = \
                [duration for duration in
                 common.global_variables.db_work_day_durations[tenant_key] if
                 duration.description == description][0]
            duration_key = duration.work_day_duration_key
            hours_lower = duration.hours_lower
            hours_upper = duration.hours_upper

        duration_icon = f"{static_url}{DURATION_ICON_DIR}{tenant_key}/{duration_key}.jpg"

        work_day_duration_response.append(
            WorkDayDurationStatsResponse(description=description, member_count=member_count,
                                         hours_lower=hours_lower, hours_upper=hours_upper,
                                         work_day_duration_key=duration_key, icon_path=duration_icon))
    return work_day_duration_response


def get_daily_attendance(query: QueryModel, es_index):
    """
    Calculates daily attendance stats for given date while applying filters, sorting and pagination
    Args:
        es_index (String): ES index to use for querying
        query (QueryModel): queryModel object to use for setting filters, sorting and pagination
    Returns:
        List of attendance data for given date
    """
    attendance_records = es_retriever.get_in_out_records_from_es(query, es_index, es_person_keyword)
    attendance = []
    for date, member_attendance in attendance_records.items():
        for member_id, time_values in member_attendance.items():
            if member_id in common.global_variables.db_member_names[query.tenant_key]:
                record = create_daily_attendance_stats_response(query.tenant_key, member_id, time_values,
                                                                query.time_zone)
                if record:
                    attendance.append(record)
    return get_sorted_and_paginated_result(attendance, query), len(attendance)


def get_office_hours(in_and_out, time_zone):
    start_time = datetime(2000, 1, 1, minute=0, hour=0)
    office_hours = datetime(2000, 1, 1, minute=0, hour=0).timestamp()
    previous_day = None
    day_in_time, day_out_time = None, None
    for record in in_and_out:
        current_datetime = get_formatted_date(record[1], time_zone)
        current_day = current_datetime.date()
        if current_day != previous_day:
            if day_in_time and day_out_time:
                office_hours = office_hours + day_out_time - day_in_time
            day_in_time, day_out_time = None, None
            day_in_time = current_datetime.timestamp()
            previous_day = current_day
        else:
            day_out_time = current_datetime.timestamp()
    if day_in_time and day_out_time and datetime.fromtimestamp(office_hours) == start_time:
        office_hours = office_hours + day_out_time - day_in_time
    difference = datetime.fromtimestamp(office_hours) - start_time
    hours = difference.days * 24 + difference.seconds // 3600
    minutes = (difference.seconds // 60) % 60
    duration = str(hours).zfill(2) + ":" + str(minutes).zfill(2)
    return duration


def extract_attendance_datetime(in_and_out, next_day_in_and_out, time_zone, continuous_attendance, tenant_key,
                                system_in_duration):
    attendance_data, in_index, last_record_time, all_in_and_outs = get_in_out_times(in_and_out, time_zone)
    status = in_and_out[-1].sign_in_status
    if not attendance_data.in_time:
        return

    if not attendance_data.out_time or (next_day_in_and_out and continuous_attendance and in_and_out[-1].sign_in_status
                                        and not in_and_out[0].record_type == es_system_record_type and
                                        not next_day_in_and_out[0].sign_in_status):
        if not next_day_in_and_out:
            return attendance_data
        status = next_day_in_and_out[-1].sign_in_status
        for values in next_day_in_and_out:
            if not values.sign_in_status:
                attendance_data.out_time = get_formatted_date(values.timestamp, time_zone)
                out_index = next_day_in_and_out.index(values)
                attendance_data.out_camera = values.camera_id
                attendance_data.out_geo_info = values.geo_stamp
                attendance_data.out_geo_fence = values.geo_fence
                all_in_and_outs = in_and_out[in_index:] + next_day_in_and_out[:out_index + 1]
                last_record_time = get_formatted_date(all_in_and_outs[-1].timestamp, time_zone)
                break
    if not attendance_data.out_time:
        return attendance_data
    attendance_data.working_hours, attendance_data.work_day_duration = get_working_hours(
        all_in_and_outs, time_zone, continuous_attendance, tenant_key)
    attendance_data.attendance_status = status
    difference = (last_record_time - attendance_data.in_time)
    hours = difference.days * 24 + difference.seconds // 3600
    minutes = (difference.seconds // 60) % 60
    attendance_data.duration = str(hours).zfill(2) + ":" + str(minutes).zfill(2)
    attendance_data.present_days = 1
    if system_in_duration:
        attendance_data.present_days = 0
    return attendance_data


def get_in_out_devices(tenant_key, in_camera, out_camera):
    in_location = NO_DATA
    out_location = NO_DATA
    in_device = NO_DATA
    out_device = NO_DATA

    if in_camera and in_camera.lower() in common.global_variables.db_camera_locations[tenant_key]:
        in_location = common.global_variables.db_camera_locations[tenant_key][in_camera.lower()]

    if out_camera and out_camera.lower() in common.global_variables.db_camera_locations[tenant_key]:
        out_location = common.global_variables.db_camera_locations[tenant_key][out_camera.lower()]

    if in_camera in common.global_variables.db_in_out_cameras[tenant_key]['mobile']:
        in_device = \
            [camera.ip for camera in common.global_variables.db_cameras[tenant_key] if camera.camera_id == in_camera][0]
    if out_camera in common.global_variables.db_in_out_cameras[tenant_key]['mobile']:
        out_device = \
            [camera.ip for camera in common.global_variables.db_cameras[tenant_key] if camera.camera_id == out_camera][
                0]

    return in_location, out_location, in_device, out_device


def get_task_time(time_values, time_zone):
    attendance_data, _, _, _ = get_in_out_times(time_values, time_zone)
    if not attendance_data.in_time:
        return
    record_date = attendance_data.in_time.date()
    if not attendance_data.out_time:
        return record_date, 0
    difference = (attendance_data.out_time - attendance_data.in_time)
    minutes = (difference.seconds // 60)
    return record_date, minutes


def create_daily_attendance_stats_response(tenant_key, member_id, time_values, time_zone):
    results = get_task_time(time_values, time_zone)
    if not results:
        return
    record_date, minutes = results
    project_name, email = NO_DATA, NO_DATA
    email = [member.email for member in common.global_variables.db_users[tenant_key] if member.member_id == member_id]
    if email:
        email = email[0]
    member_project_id = \
        [member.project_key for member in common.global_variables.db_users[tenant_key] if
         member.member_id == member_id][0]
    if member_project_id:
        project_names = [project.project_code for project in common.global_variables.db_projects[tenant_key] if
                         project.project_key == member_project_id]
        if project_names:
            project_name = project_names[0]
    tasks = [Task(**{"minutes": minutes})]
    projects = [WorkProject(**{"tasks": tasks, "project_name": project_name, "project_id": member_project_id})]
    if member_id in common.global_variables.db_member_names[tenant_key]:
        record = DailyAttendanceResponse(date_tracked=record_date,
                                         member_id=member_id,
                                         email=email,
                                         first_name=common.global_variables.get_id_from_key(
                                             common.global_variables.db_member_names[tenant_key], member_id)[0],
                                         last_name=common.global_variables.get_id_from_key(
                                             common.global_variables.db_member_names[tenant_key], member_id)[1],
                                         projects=projects,
                                         total_working_minutes=minutes)
        return record


def create_vehicle_attendance_response(results, query: QueryModel, summary=False):
    attendance = []
    for result in results:

        if not result:
            continue
        if len(result) == 4:
            in_time, in_camera, _, plate_number = result
            out_time, out_date, duration, working_hours, attendance_status, present_days, out_camera = None, None, zero_hours, zero_hours, True, 1, NO_DATA

        else:
            in_time, out_time, duration, working_hours, attendance_status, present_days, _, in_camera, out_camera, _, _, plate_number = result
        record_date = in_time.date()

        in_location, out_location, in_device, out_device = get_in_out_devices(query.tenant_key, in_camera, out_camera)
        record = VehicleAttendanceResponse(plate_number=plate_number,
                                           province=common.global_variables.get_id_from_key(
                                               common.global_variables.db_vehicle_data[query.tenant_key], plate_number)[
                                               0],
                                           date=record_date,
                                           attendance_status=attendance_status,
                                           present_days=present_days,
                                           owner_name=common.global_variables.get_id_from_key(
                                               common.global_variables.db_vehicle_data[query.tenant_key], plate_number)[
                                               1],

                                           owner_company=common.global_variables.get_id_from_key(
                                               common.global_variables.db_vehicle_data[query.tenant_key], plate_number)[
                                               2],

                                           in_time=in_time, out_time=out_time, hours=duration,
                                           working_hours=working_hours,
                                           in_location=in_location, out_location=out_location)
        attendance.append(record)

    if summary:
        return attendance
    return get_sorted_and_paginated_result(attendance, query), len(attendance)


def get_livestream_response(db, camera_ids, tenant_key, time_zone, window, sort):
    try:
        tenant_key, tenant_es_indices, tenant_tz = get_tenant_data(tenant_key)
        if not tenant_key:
            return []
        filter_values = {start_date_param: int((datetime.now() - timedelta(0, window)).timestamp() * 1000),
                         end_date_param: int(datetime.now().timestamp() * 1000), time_zone_param: time_zone}
        query = update_filters_in_query(QueryModel(), camera_ids, None, filter_values, tenant_tz, tenant_key)
        stranger_image_paths = {}

        db_strangers = db.query(Stranger).filter(
            Stranger.tenant_key == tenant_key).all()
        for stranger in db_strangers:
            stranger_image_paths["STR" + format(stranger.id, '03d')] = stranger.image_path
        return get_livestream(query, sort, tenant_es_indices.member_logs, tenant_es_indices.stranger_logs,
                              stranger_image_paths)
    except Exception as ex:
        print(ex)
