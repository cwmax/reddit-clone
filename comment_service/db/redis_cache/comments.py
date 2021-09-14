import pickle

import snappy

from comment_service.main import redis_cache
from comment_service.schemas.comments import CommentModel, CommentInfoCache


def get_comment_info_cache_name_and_key(post_id: int, comment_id: int) -> (str, str):
    name = f'{post_id}'
    key = f'{comment_id}'
    return name, key


async def cache_comment(comment: CommentModel) -> None:
    name, key = get_comment_info_cache_name_and_key(post_id=comment.post_id, comment_id=comment.id)
    comment_info_cache_value = CommentInfoCache(**comment.dict()).dict()
    await redis_cache.hset(name, key, comment_info_cache_value)
