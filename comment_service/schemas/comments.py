from typing import Optional
import datetime

from pydantic import BaseModel


class CommentInfoCache(BaseModel):
    content: str
    author_id: int
    parent_comment_id: int
    post_id: int
    is_deleted = False


class CommentInfo(CommentInfoCache):
    created_at = datetime.datetime.utcnow()


class CommentModel(CommentInfo):
    id: int
