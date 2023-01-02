from datetime import datetime
from operator import itemgetter

import common.global_variables
from apimodel.models import QueryModel
from apimodel.params import AttendanceStatus, AttendanceSortingParam, PresentStatus
from common.string_constants import date_format, NO_DATA, time_format, sign_in_status, sign_out_status, no_out_note, \
    not_categorized, indeterminate_work_duration, zero_hours
from controller.results_creator import get_duration_key
from services.results_creator_helper import fill_day_and_hour

column_date = "Date"
column_first_name = "First name"
column_last_name = "Last name"
column_in_date = "In date"
column_in_time = "In time"
column_out_date = "Out date"
column_out_time = "Out time"
column_working_hours = "Working hours"
column_office_hours = "Office hours"
column_work_day_duration = "Work day duration"
column_status = "Status"
column_notes = "Notes"
column_member_id = "Member ID"
total_present_days = "Total present days"
total_hours_worked = "Total hours worked"
average_hours_worked = "Average hours worked"
sorting_param_map = {AttendanceSortingParam.DATE: column_date,
                     AttendanceSortingParam.FIRST_NAME: column_first_name,
                     AttendanceSortingParam.LAST_NAME: column_last_name,
                     AttendanceSortingParam.MEMBER_ID: column_member_id,
                     AttendanceSortingParam.IN_DATE: column_in_date,
                     AttendanceSortingParam.IN_TIME: column_in_time,
                     AttendanceSortingParam.OUT_DATE: column_out_date,
                     AttendanceSortingParam.OUT_TIME: column_out_time,
                     AttendanceSortingParam.WORKING_HOURS: column_working_hours,
                     AttendanceSortingParam.HOURS: column_office_hours,
                     AttendanceSortingParam.WORK_DAY_DURATION: column_work_day_duration,
                     AttendanceSortingParam.ATTENDANCE_STATUS: column_status}


def get_job_category(member_id, tenant_key):
    """
    Get the job category code based on the member's title id
    :param member_id: employee ID
    :param tenant_key: tenant primary key
    :return:
    """
    try:
        title_key = \
            [member.title_key for member in common.global_variables.db_users[tenant_key] if
             member.member_id == member_id][
                0]
        if title_key in common.global_variables.db_member_titles:
            title = [title for title in common.global_variables.db_member_titles[tenant_key] if
                     title.title_key == title_key][0]

            category_code = \
                [category.category_code for category in common.global_variables.db_job_categories[tenant_key] if
                 category.category_key == title.job_category_key][0]
            return category_code, title.title_code
    except IndexError:
        pass
    return not_categorized, not_categorized


def update_category_data(category_data, title_data, member_id, query):
    job_category_code, title_code = get_job_category(member_id, query.tenant_key)
    if job_category_code not in category_data:
        category_data[job_category_code] = 1
    else:
        category_data[job_category_code] += 1

    if title_code not in title_data:
        title_data[title_code] = 1
    else:
        title_data[title_code] += 1

    return category_data, title_data


def get_attendance_report_data(result):
    out_time, out_date, attendance_status, working_hours, duration, notes, work_day_duration = \
        NO_DATA, NO_DATA, sign_in_status, zero_hours, zero_hours, no_out_note, None

    if result.out_time:
        out_time = datetime.strftime(result.out_time, time_format)
        out_date = datetime.strftime(result.out_time, date_format)
        attendance_status = sign_in_status if result.attendance_status else sign_out_status
        working_hours, duration = result.working_hours, result.duration
        notes = NO_DATA
        work_day_duration = result.work_day_duration
    in_time = datetime.strftime(result.in_time, time_format)
    in_date = datetime.strftime(result.in_time, date_format)
    member_id = result.member_id
    if result.out_time:
        result.out_date = result.out_time.date()

    return in_date, out_date, in_time, out_time, attendance_status, work_day_duration, working_hours, duration, notes, member_id


def add_absent_member_records_report(results, query):
    absent_records = []
    all_dates = fill_day_and_hour(query, "day")
    for request_date in all_dates:
        request_date = str(request_date.date())
        present_members = [result[3] for result in results if result[0] == request_date]
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

            absent_records.append(
                [request_date, first_name, last_name, member_id, "-", "-", "-", "-", "-",
                 "-", "-", "-", "-"])
    return absent_records


def update_attendance_report_rows(attendance_status_filter, work_day_durations_filter, present_status_filter, report_rows, query, headers):
    if attendance_status_filter == AttendanceStatus.BOTH and work_day_durations_filter == [] and not \
            present_status_filter==PresentStatus.PRESENT:
        absent_records = add_absent_member_records_report(report_rows, query)
        report_rows.extend(absent_records)
        if present_status_filter == PresentStatus.ABSENT:
            report_rows=absent_records

    if query.sort_param in sorting_param_map:
        reverse = True if query.sort_order == "desc" else False
        sorting_param_idx = headers[0].index(sorting_param_map[query.sort_param])
        rows_with_none_type = [row for row in report_rows if row[sorting_param_idx] is None]
        rows_without_none_type = [row for row in report_rows if row not in rows_with_none_type]
        rows_without_none_type.sort(key=itemgetter(sorting_param_idx), reverse=reverse)
        report_rows = rows_without_none_type + rows_with_none_type
    return report_rows


def get_member_attendance_for_report(results, query: QueryModel, attendance_status_filter=AttendanceStatus.BOTH,
                                     work_day_durations_filter=None, present_status_filter=PresentStatus.BOTH):
    """
    Calculates member attendance for given date while applying filters, sorting and pagination and creates response
    structured for report
    Args:
        results (String): attendance results
        query (QueryModel): queryModel object to use for setting filters, sorting and pagination
    Returns:
        List of attendance data for given date
        :param attendance_status_filter:
        :param results:
        :param query:
        :param work_day_durations_filter:
    """
    headers = [[column_date, column_first_name, column_last_name, column_member_id, column_in_date, column_in_time, column_out_date,
                column_out_time, column_working_hours, column_office_hours, column_work_day_duration, column_status,
                column_notes]]
    report_rows = []
    category_data = {}
    title_data = {}

    for result in results:
        if not result:
            continue

        in_date, out_date, in_time, out_time, attendance_status, work_day_duration, working_hours, duration, notes, member_id = get_attendance_report_data(
            result)
        status_value = AttendanceStatus.IN if attendance_status == sign_in_status else AttendanceStatus.OUT
        if attendance_status_filter != AttendanceStatus.BOTH and attendance_status_filter != status_value:
            continue

        if work_day_durations_filter and get_duration_key(work_day_duration, query) not in [int(key) for key in
                                                                                            work_day_durations_filter.split(
                                                                                                ",")]:
            continue

        first_name = common.global_variables.get_id_from_key(
            common.global_variables.db_member_names[query.tenant_key], member_id)[0]
        last_name = common.global_variables.get_id_from_key(
            common.global_variables.db_member_names[query.tenant_key], member_id)[1]
        report_rows.append([in_date, first_name, last_name, member_id, in_date, in_time, out_date, out_time,
                            working_hours, duration, work_day_duration, attendance_status, notes])
        category_data, title_data = update_category_data(category_data, title_data, member_id, query)
    report_rows = update_attendance_report_rows(attendance_status_filter, work_day_durations_filter, present_status_filter,
                                                report_rows, query, headers)
    return headers + report_rows, category_data, title_data


def get_report_row_data(query, member_id, duration_descriptions, working_hours):
    first_name = common.global_variables.get_id_from_key(
        common.global_variables.db_member_names[query.tenant_key], member_id)[0]
    last_name = common.global_variables.get_id_from_key(
        common.global_variables.db_member_names[query.tenant_key], member_id)[1]
    wdd_list = [0] * len(duration_descriptions)
    if working_hours == ' ':
        working_minutes = 0
    else:
        working_minutes = int(working_hours.split(":")[0]) * 60 + int(working_hours.split(":")[1])
    return first_name, last_name, wdd_list, working_minutes


def get_report_rows(results, attendance_status_filter, work_day_durations_filter, query, duration_descriptions,
                    desc_indices):
    report_rows = []
    member_row_idx = {}
    for result in results:
        if not result:
            continue

        _, _, _, _, attendance_status, work_day_duration, working_hours, _, _, member_id = get_attendance_report_data(
            result)
        status_value = AttendanceStatus.IN if attendance_status == sign_in_status else AttendanceStatus.OUT
        if attendance_status_filter != AttendanceStatus.BOTH and attendance_status_filter != status_value:
            continue

        if work_day_durations_filter and get_duration_key(work_day_duration, query) not in [int(key) for key in
                                                                                            work_day_durations_filter.split(
                                                                                                ",")]:
            continue
        if not work_day_duration:
            work_day_duration = no_out_note

        first_name, last_name, wdd_list, working_minutes = get_report_row_data(query, member_id, duration_descriptions,
                                                                               working_hours)


        if member_id not in member_row_idx:
            member_row_idx[member_id] = len(report_rows)
            report_rows.append(
                [member_id, first_name, last_name, 0, 0, 0] + wdd_list)
        report_rows[member_row_idx[member_id]][desc_indices[total_hours_worked]] += working_minutes
        report_rows[member_row_idx[member_id]][desc_indices[average_hours_worked]] += working_minutes
        report_rows[member_row_idx[member_id]][desc_indices[total_present_days]] += 1
        report_rows[member_row_idx[member_id]][desc_indices[work_day_duration]] += 1
    return report_rows


def get_work_day_durations_for_report(results, query: QueryModel, attendance_status_filter=AttendanceStatus.BOTH,
                                      work_day_durations_filter=None):
    """
    Calculates work_day_durations for given date while applying filters, sorting and pagination and creates response
    structured for report
    Args:
        results (String): attendance results
        query (QueryModel): queryModel object to use for setting filters, sorting and pagination
    Returns:
        List of work day durations data for given date
        :param attendance_status_filter:
        :param results:
        :param query:
        :param work_day_durations_filter:
    """

    try:
        durations = common.global_variables.db_work_day_durations[query.tenant_key]
    except KeyError:
        durations = []
    duration_descriptions = []
    tenant_work_durations = {}
    for duration in durations:
        duration_descriptions.append(duration.description)
        tenant_work_durations[duration.description] = duration

    duration_descriptions.append(indeterminate_work_duration)
    duration_descriptions.append(no_out_note)
    inital_headers = [column_member_id, column_first_name, column_last_name, total_present_days,
                      total_hours_worked, average_hours_worked]
    headers = [inital_headers + duration_descriptions]
    desc_indices = {}
    for idx, val in enumerate(headers[0]):
        desc_indices[val] = idx
    report_rows = get_report_rows(results, attendance_status_filter, work_day_durations_filter, query,
                                  duration_descriptions,
                                  desc_indices)

    for record in report_rows:
        record[desc_indices[total_hours_worked]] = round((record[desc_indices[total_hours_worked]] / 60), 2)
        record[desc_indices[average_hours_worked]] = round((record[desc_indices[average_hours_worked]] / 60 /
                                                            record[desc_indices[total_present_days]]), 2)
    for idx, desc in enumerate(headers[0]):
        if desc not in [no_out_note, indeterminate_work_duration] + inital_headers:
            duration = tenant_work_durations[desc]
            headers[0][idx] = f'{duration.description}     ({"%g" % duration.hours_lower}-{"%g" % (duration.hours_upper)})'
    return headers + report_rows
