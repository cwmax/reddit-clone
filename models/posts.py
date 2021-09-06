import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean

from .core import Base


class Posts(Base):
    __tablename__ = 'posts'
    id = Column(Integer,primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    title = Column(String, unique=True, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    site_id = Column(Integer, ForeignKey('sites.id'), nullable=False)
    content = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

