
import datetime

from common.config_manager import get_config

es_person_keyword = "person_id.keyword"
es_camera_keyword = "camera_id.keyword"
es_camera_id = "camera_id"
es_camera_key = "camera_key"
es_person_id = "person_id"
es_member_type = "member_type"
es_timestamp = "time_stamp"
es_image_path = 'image_path'
es_notification_status = 'notification_read'
es_video_path = 'video_path'
es_number_plate = 'plate_number'
es_province = 'province'
es_plate_number_keyword = 'plate_number.keyword'
es_province_keyword = 'province.keyword'
es_sign_in = "sign_in"
es_deleted = "deleted"
es_address = "address"
es_longitude = "longitude"
es_latitude = "latitude"
es_accuracy = "accuracy"
es_speed = "speed"
es_bearing = "bearing"
es_geo_fence_key = "geo_fence_key"
es_record_type = "record_type"
es_record_type_keyword = "record_type.keyword"
es_system_record_type = "S"
es_manual_record_type = "M"
es_real_record_type = "R"

es_boolean_data_type = "boolean"
es_integer_data_type = "integer"
es_text_data_type = "text"
es_date_data_type = "date"
es_long_data_type = "long"

response_member_id = "member_id"
response_location = "location"
response_first_name = "first_name"
response_last_name = "last_name"
response_timestamp = "timestamp"

zero_hours = "00:00"
datetime_format = "%Y-%m-%dT%H:%M:%S%z"
datetime_format_without_tz = "%Y-%m-%dT%H:%M:%S"
datetime_format_with_milliseconds = '%Y-%m-%dT%H:%M:%S.%f+00:00'
NO_DATA = " "
not_available = "N/A"
DEFAULT = "default"
sign_in_status = "IN"
sign_out_status = "OUT"
no_out_note = "No OUT records"
default_timezone = get_config("default_timezone")

REGULAR_STRANGER_FREQUENCY = 'regular_stranger_frequency'
REGULAR_UNREGISTERED_VEHICLE_FREQUENCY = 'regular_unregistered_vehicle_frequency'
ACCESS_TOKEN_EXPIRE_MINUTES = 'access_token_expiry_minutes'
CONTINUOUS_ATTENDANCE_METHOD = 'continuous_attendance_method'
SHIFT_START_TIME = 'night_shift_start_time'
SPOOF_CHECK = "spoof_check"
MOBILE_CAMERA_KEY = "mobile_camera_key"

# static folder
DURATION_ICON_DIR = "/duration_icons/"
CAMERA_IMAGE_DIR = "/cameras/"
indeterminate_work_duration = "Indeterminate"
not_categorized = "Not categorized"
default_work_duration_key = -1

date_format = "%Y-%m-%d"
time_format = "%H:%M"
kriyo_sync = "kriyo_sync"
door_open = "door_open"
stranger_refiner = "stranger_refiner"
data_archive = "data_archive"
alert_clip_manage = "alert_clip_manage"
manage_api_token = "manage_api_token"
system_records = "system_records"

# chart data
work_day_attendance_breakdown = "Breakdown by work day duration"
job_category_attendance_breakdown = "Breakdown by job category"
job_title_attendance_breakdown = "Breakdown by job title"
day_count = 'Day count'
ONE_DAY_TIMEDELTA = datetime.timedelta(hours=23, minutes=59, seconds=59)

# api common
user_tenant_string = 'user_tenant'
user_group_key_string = 'user_group_key'
user_key_string = "user_key"

# scoping
camera_keys_scope = "camera_keys"
user_title_attr = "title_key"
user_project_attr = "project_key"
no_access_message = "No access to this content"
created_date_col = "created_datetime"
modified_date_col = "modified_datetime"
created_user_col = "created_user"
modified_user_col = "modified_user"
stranger_id_prefix = "STR"

# spoofing
spoof_status = "status"
spoof_api_response = "Spoof"
real_api_response = "Real"
no_face_response = "No face"

# vehicle counts
car_string, motorcycle_string, van_string, bus_string, tuktuk_string, truck_string, person_string = \
    "car", "motorcycle", "van", "bus", "tuktuk", "truck", "person"

# common parameters
last_record_param = "last_record"
max_records_param = "max_records"
sorting_order_param = "sorting_order"

start_date_param = "start_date"
end_date_param = "end_date"
time_zone_param = "time_zone"

db_instance = "db"
active_user = "user"
active_admin = "admin"

shift_type_param = "shift_type"
active_status_param = "active_status"
user_group_keys_param = "user_group_keys"
owner_keys_filter = "owner_keys"
company_keys_filter = "company_keys"
provinces_filter = "provinces"
plate_numbers_filter = "plate_numbers"
camera_ids_filter = "camera_ids"

work_day_durations_filter = "work_day_durations"
sign_in_status_filter = "sign_in_status"
member_ids_filter = "member_ids"
record_type_filter = "record_type"
is_last_seen_value = "is_last_seen"
regular_value = "regular"
present_status_filter = "present_status"

aggregate_period_filter = "aggregate_period"
object_classes_filter = "object_classes"

title_filter = "title_keys"
project_filter = "project_keys"
job_category_filter = "job_category_keys"
location_filter = "location_key"
gender_filter = "gender_types"
age_filter = "age_category_ids"

face_service_param = "face_service"
stranger_service_param = "stranger_service"
face_es_log_service_param = "face_es_log_service"
face_alert_service_param = "face_alert_service"
face_tracking_service_param = "face_tracking_service"
number_plate_service_param = "number_plate_service"
face_count_service_param = "face_count_service"
vehicle_count_service_param = "vehicle_count_service"
vehicle_service_param = "vehicle_service"
vehicle_tracking_service_param = "vehicle_tracking_service"
np_es_log_service_param = "np_es_log_service"
np_tracking_service_param = "np_tracking_service"

# camera_types
mobile_device_type = "mobile"

db_user_key = "user_key"
db_login_history_time = "logged_in_out_datetime"
db_login_history_is_login = "is_login"
db_token_id = "id"
db_token_expiry = "token_expiry"
db_user_token = "token"

# geo fence types
polygon_fence = "P"
circle_fence = "C"

admin_user_group = "Admin"

# ID card verification
card_commons = ["GEO", "GFO", "GBO", "PERSON", "FIRST", "LAST", "NAME", "SEX", "DATE", "BIRTH", "EXPIRY", "IDENTITY",
                "CARD", "SIGNATURE"]
card_common_equal = ["GO", "OF"]
dot_date_regex = '(\d{2}[.|:]\d{2}[.|:]\d{4})'
no_dot_date_regex = '(\d{8})'
one_dot_right_date_regex = '(\d{4}[.|:]\d{4})'
one_dot_left_date_regex = '(\d{2}[.|:]\d{6})'
personal_number_regex = '(\d{11})'
all_caps_regex = r'[A-Z]+'
card_number_regex = r'(\d{2}[A-Z]{2}\d{5})'
card_number_i_left_regex = r'(\d{2}1[A-Z]{1}\d{5})'
card_number_i_right_regex = r'(\d{2}[A-Z]1{1}\d{5})'
dob_item = "dob"
expiry_item = "expiry"
first_name_item = "first_name"
last_name_item = "last_name"
card_number_item = "card_number"
personal_number_item = "personal_number"

admin_group_keys_param = "admin_group_keys_filter"
admin_group_key_string = "admin_group_key"
admin_key_string = "admin_key"

login_status_param = "login_status"
device_param = "device"
text_search_param = "text_search"
