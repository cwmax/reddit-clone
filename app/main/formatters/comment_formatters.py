from typing import Dict, List

from app.schemas.comments import CommentInfo
from app.models import Comments, Users


def format_comment_contents_and_order(comment: Comments, user: Users,
                                      comment_order: Dict[int, List[int]],
                                      comment_contents: Dict[int, CommentInfo],
                                      comment_indent_layer: Dict[int, int]) \
        -> (Dict[int, List[int]], Dict[int, CommentInfo]):
    comment_id = comment.id
    parent_comment_id = comment.parent_comment_id
    commentContent = CommentInfo(username=user.user_name,
                                 content=comment.content,
                                 upvote_count=0)

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
