from typing import Optional

from flask_login import current_user

from app.models import CommentEvents


def check_user_comment_existing_vote(comment_id: int, user_id: Optional[int] = None) -> (Optional[CommentEvents], bool):
    if user_id is None:
        user_id = current_user.id
    res = CommentEvents.query\
        .filter_by(comment_id=comment_id)\
        .filter_by(user_id=user_id)\
        .filter_by(event_name='vote').first()

    if res is not None:
        return res, True
    return res, False
