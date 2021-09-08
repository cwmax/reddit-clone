import os


class Config:
    SQLALCHEMY_DATABASE_URI = f'postgresql://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PW")}' \
                                         f'@{os.environ.get("POSTGRES_HOST")}/{os.environ.get("POSTGRES_DB")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', '1234abcd')
    REDIS_URL = os.environ.get('REDIS_URL')