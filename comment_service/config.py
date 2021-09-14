import os


class Config:
    POSTGRES_URI = os.environ.get('POSTGRES_URI')
    POSTGRES_MIN_CON = os.environ.get('POSTGRES_MIN_CON', 1)
    POSTGRES_MAX_CON = os.environ.get('POSTGRES_MAX_CON', 10)
