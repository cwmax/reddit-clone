from typing import Dict, List

from sqlalchemy import func, text

from app.schemas.comments import CommentInfo
from app.models import Comments, Users, CommentEvents
from app import db
from app.main.validators.comment_vote_validators import check_user_comment_existing_vote


def get_comment_final_upvote_count(comment_id: int) -> int:
    vote_count_query = """SELECT sum(sub.vote_value) as vote_count
    FROM (SELECT CASE WHEN event_value = 'upvote' THEN 1
                 WHEN event_value = 'downvote' then -1 END as vote_value
        from comment_events
        where comment_id = :comment_id AND event_name = 'vote'
    ) sub"""
    with db.engine.connect() as conn:
        res = conn.execute(text(vote_count_query), {'comment_id': comment_id}).fetchone()
    if res is None:
        return 0
    vote_count = res[0]
    if vote_count is None:
        return 0
    return vote_count


def format_comment_contents_and_order(comment: Comments, user: Users,
                                      comment_order: Dict[int, List[int]],
                                      comment_contents: Dict[int, CommentInfo],
                                      comment_indent_layer: Dict[int, int]) \
        -> (Dict[int, List[int]], Dict[int, CommentInfo]):
    comment_id = comment.id
    parent_comment_id = comment.parent_comment_id
    res, ok = check_user_comment_existing_vote(comment_id, user.id)
    user_comment_upvote = None
    if ok:
        user_comment_upvote = True if res.event_value == 'upvote' else False

    upvote_count = get_comment_final_upvote_count(comment_id)
    commentContent = CommentInfo(username=user.user_name,
                                 content=comment.content,
                                 upvote_count=upvote_count,
                                 user_comment_upvote=user_comment_upvote)

    comment_order.setdefault(parent_comment_id, [])
    comment_indent_layer.setdefault(parent_comment_id, 0)

    comment_order[parent_comment_id].append(comment_id)
    comment_contents[comment_id] = commentContent
    comment_indent_layer[comment_id] = comment_indent_layer[parent_comment_id] + 1

    return comment_order, comment_contents, comment_indent_layer


def format_comments(comments_and_users) -> (Dict[int, List[int]], Dict[int, CommentInfo], Dict[int, int]):
    comment_order = {}
    comment_contents = {}
    comment_indent_layer = {}
    if comments_and_users is not None:
        for comment, user in comments_and_users:
            comment_order, comment_contents, comment_indent_layer = format_comment_contents_and_order(comment, user,
                                                                                                      comment_order,
                                                                                                      comment_contents,
                                                                                                      comment_indent_layer)
    return comment_order, comment_contents, comment_indent_layer
