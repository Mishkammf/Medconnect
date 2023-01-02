

import common.global_variables
from exceptions.custom_exceptions import RequiredParameterException, InvalidInputException


def get_tenant_data(tenant_key):
    if tenant_key not in common.global_variables.db_tenant_config.keys():
        common.global_variables.update_global_tenant_config(tenant_key)
    tenant_config = common.global_variables.get_id_from_key(common.global_variables.db_tenant_config,
                                                            tenant_key)
    if tenant_config == -1 or not tenant_config[0]:
        return None, None, None
    return tenant_config


def validate_required_parameters(compulsory_params):
    for value in compulsory_params:
        if value is None:
            raise RequiredParameterException()


def validate_age_category(info):
    if info.start_age > info.end_age:
        raise InvalidInputException(message="Start age must be lesser than end age")
    if info.start_age < 0 or info.end_age < 0:
        raise InvalidInputException(message="Age values must be greater than 0")

