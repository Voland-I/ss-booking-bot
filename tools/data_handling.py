import logging


def get_value_from_data_object(data_object, keys, default_value=None):
    value = default_value
    for key in keys:
        try:
            value = data_object[key]
            data_object = value
        except KeyError as error:
            logging.warning(error)
            return default_value
    return value
