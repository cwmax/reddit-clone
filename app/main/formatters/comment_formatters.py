from typing import Dict, List, Tuple, Optional

from sqlalchemy import text

from app.schemas.comments import CommentInfo
from app.models import Comments, Users
from app import db
from app.main.validators.comment_vote_validators import check_user_comment_existing_vote


def tally_final_upvotes_and_downvotes(res: List[Tuple[str, int]]):
    upvotes = 0
    downvotes = 0

    if res is None:
        return upvotes, downvotes
    if len(res) == 0:
        return upvotes, downvotes

    for vote, value in res:
        if vote == 'upvote':
            upvotes += value
        elif vote == 'downvote':
            downvotes += value

    return upvotes, downvotes


def get_comment_final_upvote_count(comment_id: int) -> int:
    vote_count_query = """SELECT event_value, count(*) as vote_count
        from comment_events
        where comment_id = :comment_id AND event_name = 'vote'
        group by event_value"""
    with db.engine.connect() as conn:
        res = conn.execute(text(vote_count_query), {'comment_id': comment_id}).fetchall()

    upvotes, downvotes = tally_final_upvotes_and_downvotes(res)

    return upvotes - downvotes


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
