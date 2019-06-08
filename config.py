import os
import sys


class EnvironmentVariableMissed(EnvironmentError):
    pass


def get_value_from_env(value_name):
    value = os.environ.get(value_name)
    if value is None:
        raise EnvironmentVariableMissed(
                f'environment variable {value_name} not found'
        )

    return value


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DEBUG = False

    BOT_NAME = get_value_from_env('BOT_NAME')

    SECRET_KEY = get_value_from_env('SECRET_KEY')
    APP_ID = get_value_from_env('APP_ID')
    APP_PASS = get_value_from_env('APP_PASSWORD')

    DB_URI = get_value_from_env('MONGODB_URI')
    DB_NAME = get_value_from_env('MONGODB_NAME')
    COLLECTION_NAME = get_value_from_env('COLLECTION_NAME')
