
from datetime import datetime
from typing import List

from pydantic import BaseModel

from apimodel.params import RecordType
from common.string_constants import zero_hours, NO_DATA


class QueryModel(BaseModel):
    start_date: datetime = None
    end_date: datetime = None
    time_zone: str = None
    member_ids: List[str] = []
    camera_ids: List[str] = []
    project_keys: List[int] = []
    job_category_keys: List[int] = []
    title_keys: List[int] = []
    gender_types: List[str] = []
    age_category_ids: List[int] = []
    plate_numbers: List[str] = []
    provinces: List[str] = []
    owner_keys: List[int] = []
    company_keys: List[int] = []
    sort_param: str = None
    sort_order: str = None
    offset: int = None
    limit: int = None
    tenant_key: int = None
    user_group_key: int = None
    omit_sys_records: bool = True
    sign_in_status: bool = None
    record_type: str = RecordType.ALL


class TenantEsIndexInfo(BaseModel):
    tenant_key: int = None
    member_logs: str = None
    stranger_logs: str = None
    unknown_logs: str = None
    api_logs: str = None
    created_datetime: datetime = None
    modified_datetime: datetime = None
    time_zone: str = None
    tenant_id: str = None


class GeoStamp(BaseModel):
    address: str = None
    latitude: float = None
    longitude: float = None
    bearing: float = None
    speed: float = None
    accuracy: float = None


class GeoInfo:
    def __init__(self, member_geo_fences, tenant_geo_fences, geo_stamp):
        self.member_geo_fences = member_geo_fences
        self.tenant_geo_fences = tenant_geo_fences
        self.geo_stamp = geo_stamp


class GeoFenceModel:
    def __init__(self, radius, center, polygon, type, geo_fence_key, is_enabled):
        self.radius = radius
        self.center = center
        self.polygon = polygon
        self.type = type
        self.geo_fence_key = geo_fence_key
        self.is_enabled = is_enabled


class AttendanceData:
    def __init__(self, times=None, cameras=None, geo_infos=None, geo_fences=None, dates=None,
                 duration=zero_hours, working_hours=zero_hours, attendance_status=True, present_days=1, work_day_duration=None):
        if dates is None:
            dates = [None, None]
        if geo_fences is None:
            geo_fences = [None, None]
        if geo_infos is None:
            geo_infos = [None, None]
        if cameras is None:
            cameras = [NO_DATA, NO_DATA]
        if times is None:
            times = [None, None]
        self.in_time = times[0]
        self.in_date = dates[0]
        self.out_time = times[1]
        self.out_date = dates[1]
        self.in_camera = cameras[0]
        self.out_camera = cameras[1]
        self.in_geo_info = geo_infos[0]
        self.out_geo_info = geo_infos[1]
        self.in_geo_fence = geo_fences[0]
        self.out_geo_fence = geo_fences[1]
        self.duration = duration
        self.working_hours =  working_hours
        self.attendance_status = attendance_status
        self.present_days  =present_days
        self.work_day_duration = work_day_duration
        self.member_id = None


class InOutData:
    def __init__(self, camera_id=None, timestamp=None, sign_in_status=None, record_type=None, geo_stamp=None, geo_fence=None):
        self.camera_id = camera_id
        self.timestamp = timestamp
        self.sign_in_status = sign_in_status
        self.record_type = record_type
        self.geo_stamp = geo_stamp
        self.geo_fence = geo_fence
