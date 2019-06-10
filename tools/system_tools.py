import os
import logging


def get_value_from_env(value_name):
    value = os.environ.get(value_name)
    if value is None:
        logging.error(f'environment variable {value_name} not found')
        return
    return value
