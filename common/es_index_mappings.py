
from common.config_manager import get_config
from common.string_constants import es_timestamp, es_member_type, es_camera_id, es_person_id, es_image_path, es_sign_in, \
    es_deleted, es_address, es_accuracy, es_latitude, es_longitude, es_geo_fence_key, \
    es_boolean_data_type, es_integer_data_type, es_text_data_type, es_date_data_type, es_long_data_type, es_record_type

member_logs_mapping = {
    "settings": {
        "max_inner_result_window": get_config("elastic_search.max_inner_result_window")
    },
    "mappings": {
        "properties": {
            es_camera_id: {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "camera_key": {
                "type": es_integer_data_type
            },
            es_sign_in: {
                "type": es_boolean_data_type
            },
            es_deleted: {
                "type": es_boolean_data_type
            },
            es_member_type: {
                "type": es_text_data_type
            },
            es_person_id: {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "person_key": {
                "type": es_long_data_type
            },
            es_timestamp: {
                "type": es_date_data_type
            },
            es_image_path: {
                "type": es_text_data_type
            },
            es_address: {
                "type": es_text_data_type
            },
            es_accuracy: {
                "type": "double"
            },
            es_latitude: {
                "type": "double"
            },
            es_longitude: {
                "type": "double"
            },
            "speed": {
                "type": "double"
            },
            "bearing": {
                "type": "double"
            },
            es_geo_fence_key: {
                "type": es_integer_data_type
            }
        }
    }
}

stranger_logs_mapping = {
    "mappings": {
        "properties": {
            es_camera_id: {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "camera_key": {
                "type": es_integer_data_type
            },
            es_image_path: {
                "type": es_text_data_type
            },
            es_member_type: {
                "type": es_text_data_type
            },
            es_person_id: {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            es_record_type: {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "person_key": {
                "type": es_long_data_type
            },
            es_timestamp: {
                "type": es_date_data_type
            }
        }
    }
}

unknown_logs_mapping = {
    "mappings": {
        "properties": {
            es_camera_id: {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "camera_key": {
                "type": es_integer_data_type
            },
            es_image_path: {
                "type": es_text_data_type
            },
            es_timestamp: {
                "type": es_date_data_type
            }
        }
    }
}

api_logs_mapping = {
    "mappings": {
        "properties": {
            "method": {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "url": {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "query_params": {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "path_params": {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "client": {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "body_params": {
                "type": "flattened"
            },
            "response": {
                "type": "flattened"
            },
            es_timestamp: {
                "type": es_date_data_type
            }
        }
    }
}

update_logs_mapping = {
    "mappings": {
        "properties": {
            "entity": {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "entity_key": {
                "type": es_integer_data_type

            },
            "attribute": {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "new_value": {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "old_value": {
                "type": es_text_data_type,
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "user_key": {
                "type": es_integer_data_type
            },
            "is_user": {
                "type": es_boolean_data_type
            },
            es_timestamp: {
                "type": es_date_data_type
            }
        }
    }
}