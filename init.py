import os

import common.global_variables
from common.config_manager import get_config

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
dir_path = os.path.dirname(os.path.realpath(__file__))

COMMON_API_PREFIX = "/api/v2"

date_time_format = '%Y-%m-%d %H:%M:%S'
static_path = get_config('backend_api.static_path')
static_url = get_config('backend_api.static_url_path')
common.global_variables.update_all_global_variables()
