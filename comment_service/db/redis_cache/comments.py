from typing import Optional, List, Dict

from comment_service.schemas.comments import (CommentModel, CommentInfoCache, CommentOrder, CommentInfoDBResponse,
                                              CommentVote)
from comment_service.main import redis_cache
from comment_service.db.utils.vote import convert_user_vote_to_value


def get_comment_info_cache_name_and_key(post_id: int, comment_id: int) -> (str, str):
    name = f'{post_id}'
    key = f'{comment_id}'
    return name, key


def get_comment_vote_cache_name_and_key(post_id: int, comment_id: int) -> (str, str):
    name = f'{post_id}_c_v'
    key = f'{comment_id}'
    return name, key


def get_comment_order_cache_name(post_id: int) -> str:
    name = f'{post_id}_c_o'
    return name


def get_redis_cache_user_vote_name_and_key(user_id: int, comment_id: int) -> (str, str):
    name = f'{comment_id}_u_v'
    key = f'{user_id}'
    return name, key


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
    if mapping != {}:
        await redis_cache.hset(name, mapping=mapping)
    return mapping


async def get_key_comment_content(post_id: int, comment_id: int) -> Optional[Dict[str, CommentInfoCache]]:
    name, key = get_comment_info_cache_name_and_key(post_id, comment_id)
    comment_contents_map = None
    comment_content = await redis_cache.hget(name, key)
    if comment_content is not None:
        comment_contents_map = {comment_id: CommentInfoCache(**comment_content)}
    return comment_contents_map


async def get_all_comment_contents(post_id: int, comment_id: int, comment_order: List[CommentOrder]) -> Optional[Dict[str, CommentInfoCache]]:
    name, key = get_comment_info_cache_name_and_key(post_id, comment_id)
    comment_contents_map = None
    keys = []
    for comment in comment_order:
        current_comment_id = comment.comment_id
        name, key = get_comment_info_cache_name_and_key(post_id, current_comment_id)
        keys.append(key)
    comment_contents = {}
    if len(keys) > 0:
        comment_contents = await redis_cache.hmget(name, keys)
    if len(comment_contents) > 0:
        comment_contents_map = {int(x): CommentInfoCache(**comment_contents[x]) for x in comment_contents}
    return comment_contents_map


async def get_cached_comment_contents(post_id: int, comment_id: int = 0, comment_order: List[CommentOrder] = []) \
        -> (Optional[Dict[str, CommentInfoCache]], bool):
    if comment_id == 0:
        comment_contents_map = await get_all_comment_contents(post_id, comment_id, comment_order)
    else:
        comment_contents_map = await get_key_comment_content(post_id, comment_id)

    ok = comment_contents_map is not None

    return comment_contents_map, ok


async def check_vote_exists_cache(user_id, comment_id: int) -> (int, ):
    name, key = get_redis_cache_user_vote_name_and_key(user_id, comment_id)
    redis_value = await redis_cache.hget(name, key)

    return redis_value


async def get_comment_vote_cache_value(post_id: int, comment_id: int) -> Optional[int]:
    name, key = get_comment_vote_cache_name_and_key(post_id, comment_id)
    comment_vote_cache_value = await redis_cache.hgetraw(name, key)
    if comment_vote_cache_value is not None:
        comment_vote_cache_value = int(comment_vote_cache_value)
    return comment_vote_cache_value


async def check_comment_votes_exists(post_id: int, comment_id: int):
    name, key = get_comment_vote_cache_name_and_key(post_id, comment_id)
    exists = await redis_cache.hexists(name, key)
    return exists


async def set_user_vote_in_cache(vote: CommentVote, comment_id: int) -> int:
    name, key = get_redis_cache_user_vote_name_and_key(vote.user_id, comment_id)
    redis_vote_value = convert_user_vote_to_value(vote)
    await redis_cache.hset(name, key, redis_vote_value)
    return redis_vote_value


async def set_comment_vote_in_cache(comment_vote_val: int, comment_id: int, post_id:int) -> None:
    name, key = get_comment_vote_cache_name_and_key(post_id, comment_id)
    await redis_cache.hsetraw(name, key, comment_vote_val)


async def update_comment_vote_in_cache(vote_change_value: int, comment_id: int, post_id:int) -> None:
    name, key = get_comment_vote_cache_name_and_key(post_id, comment_id)
    await redis_cache.hincrby(name, key, vote_change_value)


async def check_cached_comment_votes_exists(post_id: int):
    name, key = get_comment_vote_cache_name_and_key(post_id, 0)
    return await redis_cache.exists(name)


async def get_comment_votes_from_cache(post_id: int) -> Dict[str, int]:
    name, key = get_comment_vote_cache_name_and_key(post_id, 0)
    return_dict = await redis_cache.hgetallraw(name)
    for v in return_dict:
        return_dict[v] = int(return_dict[v])
    return return_dict


async def update_comment_votes_in_cache(post_id: int, comment_ids: Dict[str, int]):
    name, key = get_comment_vote_cache_name_and_key(post_id, 0)
    await redis_cache.hsetraw(name, mapping=comment_ids)
