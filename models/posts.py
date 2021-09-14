import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, UniqueConstraint

from .core import Base


class Posts(Base):
    __tablename__ = 'posts'
    __tableargs__ = (UniqueConstraint('title', 'author_id', 'site_id', name='post_title_author_site_unique'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    title = Column(String, nullable=False)
    author_id = Column(Integer, nullable=False)
    site_id = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
