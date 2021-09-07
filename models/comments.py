import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, Index

from .core import Base


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer,primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    content = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    parent_comment_id = Column(Integer, default=0, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)


Index('post_parent_comment_idx', Comments.post_id, Comments.parent_comment_id)