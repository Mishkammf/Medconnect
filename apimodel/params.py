from enum import Enum

from common.string_constants import es_real_record_type, es_manual_record_type


class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"


class SortingOrder(str, Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


class ProjectSortingParam(str, Enum):
    PROJECT_KEY = "project_key"
    PROJECT_CODE = "project_code"
    CREATED_USER = "created_user"
    MODIFIED_USER = "modified_user"


class AgeCategorySortingParam(str, Enum):
    CATEGORY_KEY = "id"


class WorkDaySortingParam(str, Enum):
    DESCRIPTION = "description"
    MINUTES_LOWER = "minutes_lower"
    MINUTES_UPPER = "minutes_upper"
    CREATED_USER = "created_user"
    MODIFIED_USER = "modified_user"


class UserTokenSortingParam(str, Enum):
    CREATED_DATE_TIME = "id"
    MODIFIED_DATE_TIME = "project_code"


class JobCategorySortingParam(str, Enum):
    CATEGORY_KEY = "category_key"
    CATEGORY_CODE = "category_code"
    CREATED_USER = "created_user"
    MODIFIED_USER = "modified_user"


class MemberTitleSortingParam(str, Enum):
    TITLE_KEY = "title_key"
    JOB_CATEGORY_KEY = "job_category_key"
    TITLE_CODE = "title_code"
    JOB_CATEGORY_CODE = "category_code"
    CREATED_USER = "created_user"
    MODIFIED_USER = "modified_user"



class MemberActivitySortingParam(str, Enum):
    MEMBER_ID = "member_id"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    LOCATION = "location"
    TIMESTAMP = "timestamp"


class AttendanceSortingParam(str, Enum):
    MEMBER_ID = "member_id"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    IN_TIME = "in_time"
    OUT_TIME = "out_time"
    IN_DATE = "in_date"
    OUT_DATE = "out_date"
    HOURS = "hours"
    WORKING_HOURS = "working_hours"
    IN_LOCATION = "in_location"
    OUT_LOCATION = "out_location"
    ATTENDANCE_STATUS = "attendance_status"
    WORK_DAY_DURATION = "work_day_duration"
    DATE = "date"
    IN_DEVICE = "in_device"
    OUT_DEVICE = "out_device"


class DailyAttendanceStatsSortingParam(str, Enum):
    MEMBER_ID = "member_id"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    IN_TIME = "in_time"
    OUT_TIME = "out_time"
    HOURS = "hours"
    DATE_TRACKED = "date_tracked"


class VehicleAttendanceSortingParam(str, Enum):
    OWNER_NAME = "owner_name"
    COMPANY = "owner_company"
    PLATE_NUMBER = "plate_number"
    PROVINCE = "province"
    IN_TIME = "in_time"
    OUT_TIME = "out_time"
    HOURS = "hours"
    IN_LOCATION = "in_location"
    OUT_LOCATION = "out_location"


class LocationSortingParam(str, Enum):
    LOCATION_LEVEL = "location_type"
    LOCATION_NAME = "location_name"
    PARENT_NAME = "parent_name"
    CREATED_USER = "created_user"
    MODIFIED_USER = "modified_user"


class StrangerActivitySortingParam(str, Enum):
    STRANGER_ID = "stranger_id"
    LOCATION = "location"
    TIMESTAMP = "timestamp"
    MEMBER_ID = "member_id"


class UnrecognizedVehicleActivitySortingParam(str, Enum):
    PLATE_NUMBER = "plate_number"
    LOCATION = "location"
    TIMESTAMP = "timestamp"


class CameraInfoSortingParam(str, Enum):
    ID = "id"
    IP = "ip"
    LOCATION = "location_name"
    NAME = "name"
    LAST_ACTIVE_TIME = "last_active_time"
    CREATED_USER = "created_user"
    MODIFIED_USER = "modified_user"


class TenantInfoSortingParam(str, Enum):
    ID = "tenant_id"
    NAME = "tenant_name"
    ORGANIZATION = "tenant_organization"
    CREATED_DATE = "created_datetime"
    MODIFIED_DATE = "modified_datetime"


class UserInfoSortingParam(str, Enum):
    USER_LOGIN_ID = "user_login_id"
    TENANT_KEY = "tenant_key"
    GROUP_KEY = "user_group_key"
    GROUP_NAME = "user_group"
    MEMBER_ID = "member_id"
    LOCATION = "location_name"
    TITLE = "sub_category_code"
    PROJECT = "project_code"
    CREATED_DATE = "created_datetime"
    MODIFIED_DATE = "modified_datetime"
    EMAIL_ADDRESS = "email"
    MOBILE_NUMBER = "mobile_number"
    FIRST_NAME = "first_name"
    CREATED_USER = "created_user"
    MODIFIED_USER = "modified_user"


class AdminInfoSortingParam(str, Enum):
    LOGIN_ID = "login_id"
    GROUP_KEY = "admin_group_key"
    GROUP_NAME = "admin_group"
    CREATED_DATE = "created_datetime"
    MODIFIED_DATE = "modified_datetime"
    EMAIL_ADDRESS = "email"
    MOBILE_NUMBER = "mobile_number"
    FIRST_NAME = "first_name"
    CREATED_USER = "created_user"
    MODIFIED_USER = "modified_user"


class AlertTimeSlotSortingParam(str, Enum):
    START_TIME = "start_time"
    END_TIME = "end_time"
    CAMERA_ID = "camera_id"


class BooleanOptions(str, Enum):
    ALL = "None"
    TRUE = "True"
    FALSE = "False"


class PersonType(str, Enum):
    ALL = "all"
    MEMBER = "member"
    STRANGER = "stranger"


class AlertNotificationSortingParam(str, Enum):
    TIMESTAMP = "timestamp"
    PERSON_ID = "person_id"
    LOCATION_NAME = "location_name"
    PERSON_NAME = "first_name"


class VehicleSortingParam(str, Enum):
    PLATE_NUMBER = "plate_number"
    PROVINCE = "province"
    OWNER_NAME = "owner_name"
    OWNER_COMPANY = "owner_company"
    CREATED_USER = "created_user"
    MODIFIED_USER = "modified_user"


class VehicleActivitySortingParam(str, Enum):
    PLATE_NUMBER = "plate_number"
    PROVINCE = "province"
    OWNER_NAME = "owner_name"
    OWNER_COMPANY = "owner_company"
    LOCATION = "location"
    TIMESTAMP = "timestamp"


class LoginHistorySortingParam(str, Enum):
    USER_LOGIN_ID = "user_login_id"
    IP_ADDRESS = "ip_address"
    LOGGED_IN_OUT_DATETIME = "logged_in_out_datetime"
    IS_LOGIN = "is_login"
    DEVICE = "device"


class LoginStatus(str, Enum):
    LOGIN = 'Login'
    LOGOUT = 'Logout'
    SESSION_EXPIRED = "Session expired"
    SESSIONS_EXCEEDED = "Sessions exceeded"
    BOTH = None


class ActiveStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BOTH = "both"

class TrialStatus(str, Enum):
    TRIAL = "trial"
    BUSINESS = "business"
    BOTH = "both"

class Device(str, Enum):
    API = "0"
    MOBILE = "2"
    WEB = "1"
    ALL = None


class AttendanceStatus(str, Enum):
    IN = "1"
    OUT = "0"
    BOTH = "2"


class PresentStatus(str, Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    BOTH = "Both"

class RecordType(str, Enum):
    MANUAL = es_manual_record_type
    REAL = es_real_record_type
    ALL = "all"


class CameraLiveStatusSortingParam(str, Enum):
    CAMERA_ID = "camera_id"
    IS_ACTIVE = "is_live"
    LAST_UPDATED_DATETIME = "last_updated_datetime"


class EscalationLevelParam(str, Enum):
    DEV = "dev"
    TECH_LEAD = "tech_lead"
    OTHER = "other"


class PipelineAdminSortingParam(str, Enum):
    ADMIN_KEY = "admin_key"
    EMAIL_ADDRESS = "email_address"
    NAME = "name"
    ESCALATION_LEVEL = "escalation_level"


class PipelineConfigSortingParam(str, Enum):
    CAMERA_ID = "camera_id"


class PipelineConfigCameraType(str, Enum):
    ALL = "all"
    FACE = "face"
    VEHICLE = "vehicle"


class UserGroupSortingParam(str, Enum):
    GROUP_NAME = "user_group"
    GROUP_KEY = "user_group_key"
    CREATED_USER = "created_user"
    MODIFIED_USER = "modified_user"
    CREATED_DATE = "created_datetime"
    MODIFIED_DATE = "modified_datetime"


class AdminGroupSortingParam(str, Enum):
    GROUP_NAME = "admin_group"
    GROUP_KEY = "admin_group_key"
    CREATED_USER = "created_user"
    MODIFIED_USER = "modified_user"
    CREATED_DATE = "created_datetime"
    MODIFIED_DATE = "modified_datetime"


class UserRoleSortingParam(str, Enum):
    USER_ROLE = "user_role"
    USER_ROLE_KEY = "user_role_key"

class AdminRoleSortingParam(str, Enum):
    ADMIN_ROLE = "admin_role"
    ADMIN_ROLE_KEY = "admin_role_key"

class AggregatePeriod(str,Enum):
    HOUR = "hour"
    MINUTE = "minute"
    NONE = "none"


class CountObject(str, Enum):
    FACE = "face"
    OBJECT = "object"


class CameraType(str, Enum):
    IN_CAMERA = "in"
    OUT_CAMERA = "out"
    MOBILE_CAMERA = "mobile"


class CountStatsSortingParam(str, Enum):
    TIMESTAMP = "timestamp"
    COUNT= "count"

