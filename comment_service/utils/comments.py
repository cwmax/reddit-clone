from typing import Dict

from comment_service.schemas.comments import CommentInfoResponse


def get_comment_indent_level(comment_content: Dict[str, CommentInfoResponse]) -> Dict[str, int]:
    comment_indent_levels = {}
    comment_indent_levels.setdefault('0', 0)
    print('comment_content input:', comment_content)
    for key in comment_content:
        comment = comment_content[key]
        comment_indent_levels[key] = comment_indent_levels[str(comment.parent_comment_id)] + 1

    return comment_indent_levels
