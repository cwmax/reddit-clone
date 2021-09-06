import datetime

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, String, Boolean, UniqueConstraint

from .core import Base


class Sites(Base):
    __tablename__ = 'sites'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False, index=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)


class UserSiteFollows(Base):
    __tablename__ = 'user_site_follows'
    id = Column(Integer, autoincrement=True, primary_key=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    site_id = Column(Integer, ForeignKey('sites.id'), nullable=False)


class UserSiteAdmins(Base):
    __tablename__ = 'user_site_admins'
    __tableargs__ = (UniqueConstraint('user_id', 'site_id', name='user_id_site_id_unique'),)
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    site_id = Column(Integer, ForeignKey('sites.id'), nullable=False)
