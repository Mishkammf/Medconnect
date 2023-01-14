
from datetime import datetime
from typing import List

from pydantic import BaseModel

from apimodel.params import RecordType
from common.string_constants import zero_hours, NO_DATA


class QueryModel(BaseModel):
    start_date: datetime = None
    end_date: datetime = None
    sort_param: str = None
    sort_order: str = None
    offset: int = None
    limit: int = None
    tenant_key: int = None
    user_group_key: int = None


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


