from typing import Dict, List

from app.schemas.comments import CommentInfo, CommentUserAndContent
from flask_login import current_user
from app import app, redis
from app.main.validators.comment_vote_validators import check_user_comment_existing_vote
from app.main.redis_cache_helpers import insert_value_into_redis_from_db, get_comment_final_upvote_count_from_db


def get_comment_final_upvote_count(post_id: int, comment_id: int) -> int:
    name = str(post_id)
    key = str(comment_id)
    redis_value = redis.hget(name, key)
    if redis_value is None:
        return insert_value_into_redis_from_db(name, key)
    try:
        upvote_count = int(redis_value.decode('utf-8'))
        return upvote_count
    except ValueError:
        app.logger.error(f'Encountered non-int value in {name}, {key}, {redis_value}')
        return get_comment_final_upvote_count_from_db(comment_id)
    except Exception as e:
        app.logger.error(f'Encountered unhandled exception {e}')
        return get_comment_final_upvote_count_from_db(comment_id)


def format_comment_contents_and_order(comment_user_info: CommentUserAndContent,
                                      comment_order: Dict[int, List[int]],
                                      comment_contents: Dict[int, CommentInfo],
                                      comment_indent_layer: Dict[int, int],
                                      post_id: int) \
        -> (Dict[int, List[int]], Dict[int, CommentInfo]):
    comment_id = comment_user_info.id
    parent_comment_id = comment_user_info.parent_comment_id
    # TODO: implement cache here
    user_comment_upvote = None
    if current_user.is_authenticated:
        res, ok = check_user_comment_existing_vote(comment_id, current_user.id)

        if ok:
            user_comment_upvote = True if res.event_value == 'upvote' else False

    upvote_count = get_comment_final_upvote_count(post_id, comment_id)

    commentContent = CommentInfo(username=comment_user_info.username,
                                 content=comment_user_info.content,
                                 parent_comment_id=comment_user_info.parent_comment_id,
                                 upvote_count=upvote_count,
                                 user_comment_upvote=user_comment_upvote)

    comment_order.setdefault(parent_comment_id, [])
    comment_indent_layer.setdefault(parent_comment_id, 0)

    comment_order[parent_comment_id].append(comment_id)
    comment_contents[comment_id] = commentContent
    comment_indent_layer[comment_id] = comment_indent_layer[parent_comment_id] + 1

    return comment_order, comment_contents, comment_indent_layer


def format_comments(comments_and_users: List[CommentUserAndContent], post_id: int) \
        -> (Dict[int, List[int]], Dict[int, CommentInfo], Dict[int, int]):
    comment_order = {}
    comment_contents = {}
    comment_indent_layer = {}

    for comment_user_info in comments_and_users:
        comment_order, comment_contents, comment_indent_layer = format_comment_contents_and_order(comment_user_info,
                                                                                                  comment_order,
                                                                                                  comment_contents,
                                                                                                  comment_indent_layer,
                                                                                                  post_id)
    return comment_order, comment_contents, comment_indent_layer
