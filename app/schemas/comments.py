import datetime
from typing import Optional

from pydantic import BaseModel


class CommentOrder(BaseModel):
    comment_id: int
    created_at: datetime.datetime


class CommentUserAndContent(BaseModel):
    username: str
    content: str
    parent_comment_id: int
    id: Optional[int]


class CommentInfo(CommentUserAndContent):
    upvote_count: int
    user_comment_upvote: Optional[bool]
