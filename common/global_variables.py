


def update_all_global_variables():
    pass


def get_id_from_key(dict_param, key):
    if key == '':
        return -1
    if key not in dict_param:
        update_all_global_variables()
    if key not in dict_param:
        return -1
    return dict_param[key]
