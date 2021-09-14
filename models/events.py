import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, Index

from .core import Base


class PostEvents(Base):
    __tablename__ = 'post_events'

    id = Column(Integer,primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    event_name = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    event_value = Column(String, nullable=False)


class CommentEvents(Base):
    __tablename__ = 'comment_events'

    id = Column(Integer,primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    event_name = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)
    comment_id = Column(Integer, ForeignKey('comments.id'), nullable=False)
    event_value = Column(String, nullable=False)


Index('comment_id_event_name_idx', CommentEvents.comment_id, CommentEvents.event_name)
Index('comment_user_event_name_idk', CommentEvents.id, CommentEvents.user_id, CommentEvents.event_name)