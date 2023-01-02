
import calendar
import collections
import re
from datetime import timedelta, datetime

import common.global_variables
from common.database.admin import Admin
from common.string_constants import datetime_format
from services.db_crud_operations import retrieve


def get_is_sign_in(tenant_key, record):
    if record.sign_in_status is not None:
        if record.sign_in_status:
            return 1
        else:
            return 0
    else:
        if record.camera_id in common.global_variables.get_id_from_key(
                common.global_variables.db_in_out_cameras[tenant_key], "in"):
            return 1
        elif record.camera_id in common.global_variables.get_id_from_key(
                common.global_variables.db_in_out_cameras[tenant_key], "out"):
            return 0
    return 2


def get_full_name(user_key, tenant_key=None, db=None):
    if not user_key:
        return None
    if tenant_key:
        user = [user for user in common.global_variables.db_users[tenant_key] if user.user_key == user_key]
    else:
        user = retrieve(db, Admin, None, Admin.admin_key == user_key, [Admin.first_name, Admin.last_name])[0]
    if not user:
        return None
    user = user[0]
    if not user.first_name:
        return None
    if not user.last_name:
        return user.first_name
    return user.first_name + " " + user.last_name


# below function can be removed by using https://pendulum.eustace.io/docs/
def fill_day_and_hour(query, interval):
    all_dates = []
    start = query.start_date
    end = query.end_date
    if interval == "day":
        step = timedelta(days=1)
    else:
        step = timedelta(hours=1)

    while start <= end:
        all_dates.append(start)
        start = start + step
    return all_dates


# below function can be removed by using https://pendulum.eustace.io/docs/
def fill_month_and_year(query, interval):
    start = query.start_date
    end = query.end_date

    all_dates = []

    while start <= end:
        all_dates.append(start)
        if interval == "month":
            start = start + timedelta(days=calendar.monthrange(start.year, start.month)[1])
        else:
            year = start.year
            if calendar.isleap(year):
                start = start + timedelta(days=366)
            else:
                start = start + timedelta(days=365)
    return all_dates


# below function can be removed by using https://pendulum.eustace.io/docs/
def fill_empty_dates(query, interval, emp_hist):
    if interval in ["day", "hour"]:
        all_dates = fill_day_and_hour(query, interval)
    else:
        all_dates = fill_month_and_year(query, interval)
    for date in all_dates:
        if date not in emp_hist:
            emp_hist[date][None] = []
    dates_to_pop = []
    for date in emp_hist:
        if date not in all_dates:
            dates_to_pop.append(date)
    for date in dates_to_pop:
        emp_hist.pop(date)

    emp_hist = collections.OrderedDict(sorted(emp_hist.items()))
    return emp_hist


# below function can be removed by using https://pendulum.eustace.io/docs/
def get_formatted_date(timestamp, time_zone, date_type=None):
    try:
        if date_type == "long":
            return datetime.fromtimestamp(int(timestamp / 1000),
                                          tz=datetime.strptime(time_zone, "%z").tzinfo)
        else:
            return datetime.strptime(timestamp[:-13] + time_zone,
                                     datetime_format) + get_tz_adjustment(time_zone)
    except ValueError:
        return datetime(year=0, month=0, day=0)


def get_location_scores(cameras):
    camera_locations = {}
    for camera in cameras:
        camera_locations[camera.camera_id] = camera.location
    sorted_cameras = {k: v for k, v in sorted(camera_locations.items(), key=lambda item: item[1])}

    score = 0
    scores = {}
    for camera_id in sorted_cameras.keys():
        scores[camera_id] = score
        score += 1

    return scores


def get_member_name_scores(sort_param, member_ids, db_members):
    if sort_param == "first_name":
        sorted_members = sorted([member for member in db_members if member.first_name], key=lambda x: x.first_name)
    else:
        sorted_members = sorted([member for member in db_members if member.last_name], key=lambda x: x.last_name)
    score = 0
    scores = {}
    for member in sorted_members:
        if member_ids:
            if member.member_id in member_ids:
                scores[member.member_id] = score
                score += 1
        else:
            scores[member.member_id] = score
            score += 1
    return scores


def get_vehicle_owner_scores(sort_param, plate_numbers, db_vehicle_data):
    if sort_param == "owner_name":
        sorted_vehicles = sorted(db_vehicle_data.items(), key=lambda item: db_vehicle_data[item[0]][1])
    else:
        sorted_vehicles = sorted(db_vehicle_data.items(), key=lambda item: db_vehicle_data[item[0]][2])
    score = 0
    scores = {}
    for plate_number, _ in sorted_vehicles:
        if plate_numbers:
            if plate_number in plate_numbers:
                scores[plate_number] = score
                score += 1
        else:
            scores[plate_number] = score
            score += 1
    return scores


def get_numerical_value(text):
    return int("".join([s for s in [char for char in text] if s.isdigit()]))


def get_alpha_num_list(key):
    return [int(c) if c.isdigit() else c for c in re.split('([0-9]+)', key)]


def sort_member_ids(members_ids):
    return sorted(members_ids, key=get_alpha_num_list)


def get_member_id_scores(tenant_key, member_ids):
    """
    Finds score for each id in given list of member ids based on alpnumerical value
    Args:
        tenant_key (int): tenant key
        member_ids ():

    Returns:

    """
    score = 0
    scores = {}
    if not member_ids:
        member_ids = [x.member_id for x in common.global_variables.db_users[tenant_key]]
    for member_id in sort_member_ids(member_ids):
        scores[member_id] = score
        score += 1
    return scores


def get_tz_adjustment(time_zone):
    tz_sign = time_zone[0]
    if tz_sign == "+":
        time_zone_adjustment = timedelta(hours=int(time_zone[1:3]), minutes=int(time_zone[4:6]))
    else:
        time_zone_adjustment = timedelta(hours=-int(time_zone[1:3]), minutes=-int(time_zone[4:6]))
    return time_zone_adjustment


def get_remaining_days(trial_start_date, trial_end_date):
    """
    Finds remaining days to end the trail
    Args:
        trial_start_date (datetime): trial starting date
        trial_end_date (datetime): trial ending date

    Returns:

    """
    remain_days = None
    if trial_start_date and trial_end_date:
        remain_days = (trial_end_date - datetime.now()).days
        if remain_days < -1:
            remain_days = -1
    return remain_days
