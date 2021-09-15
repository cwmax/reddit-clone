from typing import Optional, List, Dict

from comment_service.schemas.comments import CommentModel, CommentInfoCache, CommentOrder, CommentInfoDBResponse
from comment_service.main import redis_cache


def get_comment_info_cache_name_and_key(post_id: int, comment_id: int) -> (str, str):
    name = f'{post_id}'
    key = f'{comment_id}'
    return name, key


def get_comment_order_cache_name(post_id: int) -> str:
    name = f'{post_id}_c_o'
    return name


async def cache_comment(comment: CommentModel) -> None:
    name, key = get_comment_info_cache_name_and_key(post_id=comment.post_id, comment_id=comment.id)
    comment_info_cache_value = CommentInfoCache(**comment.dict()).dict()
    await redis_cache.hset(name, key, comment_info_cache_value)


async def get_cached_comment_order(post_id: int) -> (Optional[List[CommentOrder]], bool):
    comment_order_cache_name = get_comment_order_cache_name(post_id)
    val = await redis_cache.get(comment_order_cache_name)
    ok = val is not None
    return val, ok


async def cache_comment_order(post_id: int, comment_order: List[CommentOrder]) -> None:
    comment_order_cache_name = get_comment_order_cache_name(post_id)
    await redis_cache.set(comment_order_cache_name, comment_order)


async def cache_comment_contents(post_id: int, comment_contents: List[CommentInfoDBResponse]) \
        -> Dict[str, CommentInfoCache]:
    mapping = {}
    name, key = get_comment_info_cache_name_and_key(post_id, 0)
    for comment in comment_contents:
        comment_id = comment.id
        name, key = get_comment_info_cache_name_and_key(post_id, comment_id)
        mapping[key] = CommentInfoCache(**comment.dict())

    await redis_cache.hset(name, mapping=mapping)
    return mapping


async def get_key_comment_content(post_id: int, comment_id: int) -> Optional[Dict[int, CommentInfoCache]]:
    name, key = get_comment_info_cache_name_and_key(post_id, comment_id)
    comment_contents_map = None
    comment_content = await redis_cache.hget(name, key)
    if comment_content is not None:
        comment_contents_map = {comment_id: CommentInfoCache(**comment_content)}
    return comment_contents_map


async def get_all_comment_contents(post_id: int, comment_id: int) -> Optional[Dict[int, CommentInfoCache]]:
    name, key = get_comment_info_cache_name_and_key(post_id, comment_id)
    comment_contents_map = None
    comment_contents = await redis_cache.hgetall(name)
    if len(comment_contents) > 0:
        comment_contents_map = {int(x): CommentInfoCache(**comment_contents[x]) for x in comment_contents}
    return comment_contents_map


async def get_cached_comment_contents(post_id: int, comment_id: int = 0) -> (Optional[Dict[int, CommentInfoCache]], bool):
    if comment_id == 0:
        comment_contents_map = await get_all_comment_contents(post_id, comment_id)
    else:
        comment_contents_map = await get_key_comment_content(post_id, comment_id)

    ok = comment_contents_map is not None

    return comment_contents_map, ok
