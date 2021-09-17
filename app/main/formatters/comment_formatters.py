from typing import Dict, List

from app.schemas.comments import CommentInfo, CommentUserAndContent, CommentOrder
from app import app
from app.main.validators.comment_vote_validators import check_user_comment_existing_vote
from app.main.redis_cache_helpers import (get_upvote_count,
                                          get_comment_upvote_name_and_key)


def get_comment_final_upvote_count(post_id: int, comment_id: int) -> int:
    name, key = get_comment_upvote_name_and_key(post_id, comment_id)
    try:
        upvote_count = get_upvote_count(name, key)
        return upvote_count
    except ValueError:
        app.logger.error(f'Encountered non-int value in {name}, {key}')
    except Exception as e:
        app.logger.error(f'Encountered unhandled exception {e}')


def format_comment_contents_and_order(comment_user_info: CommentInfo,
                                      comment_order: Dict[int, List[int]],
                                      comment_contents: Dict[int, CommentInfo],
                                      comment_indent_layer: Dict[int, int],
                                      post_id: int,
                                      user_authenticated: bool,
                                      user_id: int) \
        -> (Dict[int, List[int]], Dict[int, CommentInfo]):
    comment_id = comment_user_info.id
    parent_comment_id = comment_user_info.parent_comment_id

    # user_comment_upvote = None
    # if user_authenticated:
    #     res, ok = check_user_comment_existing_vote(comment_id, user_id)
    #
    #     if ok:
    #         user_comment_upvote = True if res.event_value == 'upvote' else False
    #
    # upvote_count = get_comment_final_upvote_count(post_id, comment_id)
    # commentContent = CommentInfo(username=comment_user_info.username,
    #                              content=comment_user_info.content,
    #                              parent_comment_id=comment_user_info.parent_comment_id,
    #                              upvote_count=upvote_count,
    #                              user_comment_upvote=user_comment_upvote)

    comment_order.setdefault(parent_comment_id, [])
    comment_indent_layer.setdefault(parent_comment_id, 0)

    comment_order[parent_comment_id].append(comment_id)
    comment_contents[comment_id] = comment_user_info
    comment_indent_layer[comment_id] = comment_indent_layer[parent_comment_id] + 1

    return comment_order, comment_contents, comment_indent_layer


def format_comments(comments_and_users: List[CommentInfo], post_id: int,
                    user_authenticated: bool, user_id: int) \
        -> (Dict[int, List[int]], Dict[int, CommentInfo], Dict[int, int]):
    comment_order = {}
    comment_contents = {}
    comment_indent_layer = {}
    for comment_user_info in comments_and_users:
        comment_order, comment_contents, comment_indent_layer = format_comment_contents_and_order(comment_user_info,
                                                                                                  comment_order,
                                                                                                  comment_contents,
                                                                                                  comment_indent_layer,
                                                                                                  post_id,
                                                                                                  user_authenticated,
                                                                                                  user_id)
    return comment_order, comment_contents, comment_indent_layer


def form_comment_and_user_information(post_comment_order: List[CommentOrder],
                                      post_comment_user_and_content: List[CommentInfo]) \
        -> List[CommentInfo]:
    supplemented_post_comment_user_and_content = [CommentInfo(**{k: uc.dict().get(k)
                                                                           for k in ['username', 'content',
                                                                                     'parent_comment_id']
                                                                           },
                                                                        id=i.comment_id)
                                                  for i, uc in zip(post_comment_order, post_comment_user_and_content)]
    return supplemented_post_comment_user_and_content
