from typing import Optional

from pydantic import BaseModel


class CommentInfo(BaseModel):
    username: str
    content: str
    upvote_count: int
    user_comment_upvote: Optional[bool]
