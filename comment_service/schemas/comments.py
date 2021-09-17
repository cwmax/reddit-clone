from typing import Dict, List, Optional
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
    # upvote_count: int


class CommentInfoResponse(BaseModel):
    content: str
    username: str
    parent_comment_id: int
    post_id: int
    is_deleted = False
    upvote_count: int
    user_upvoted: Optional[bool]


class CommentInfoDBResponse(CommentInfoCache):
    id: int


class CommentInfo(CommentInfoCache):
    created_at = datetime.datetime.utcnow()


class CommentModel(CommentInfo):
    id: int


class PostCommentResponse(BaseModel):
    comment_order: List[CommentOrder]
    comment_content: Dict[int, CommentInfoResponse]
    comment_indent: Dict[int, int]


class CommentVote(BaseModel):
    user_id: int
    vote: str
    post_id: int


class CommentEvent(BaseModel):
    created_at: datetime.datetime
    event_name: str
    user_id: int
    comment_id: int
    event_value: str


class CommentEventDBEntry(CommentEvent):
    id: int
