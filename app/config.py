import os


class Config:
    SQLALCHEMY_DATABASE_URI = f'postgresql://localhost:5432/reddit'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', '1234abcd')
    REDIS_URL = os.environ.get('REDIS_URL')