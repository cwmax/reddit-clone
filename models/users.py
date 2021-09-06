import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP

from .core import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer,primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    email = Column(String, unique=True, nullable=False, index=True)
    user_name = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)

