from typing import Dict, List, Tuple
import datetime

from pydantic import BaseModel


class CommentOrder(BaseModel):
    comment_id: int
    created_at: datetime.datetime


class CommentInfoCache(BaseModel):
    content: str
    author_id: int
    parent_comment_id: int
    post_id: int
    is_deleted = False


class CommentInfoResponse(BaseModel):
    content: str
    username: str
    parent_comment_id: int
    post_id: int
    is_deleted = False


class CommentInfoDBResponse(CommentInfoCache):
    id: int


class CommentInfo(CommentInfoCache):
    created_at = datetime.datetime.utcnow()


class CommentModel(CommentInfo):
    id: int


class PostCommentResponse(BaseModel):
    comment_order: List[CommentOrder]
    comment_content: Dict[int, CommentInfoCache]
    comment_indent: Dict[int, int]
