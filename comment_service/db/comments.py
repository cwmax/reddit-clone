from typing import List, Dict
import asyncio

from comment_service.schemas.comments import CommentOrder, CommentInfoCache, CommentInfoResponse
from comment_service.db.redis_cache.comments import (get_cached_comment_order, cache_comment_order,
                                                     get_cached_comment_contents, cache_comment_contents)
from comment_service.db.crud.comments import get_comment_order_from_db, get_comment_contents_from_db


async def load_and_cache_comment_order(post_id: int) -> List[CommentOrder]:
    comment_order, ok = await get_cached_comment_order(post_id)
    if not ok:
        comment_order = await get_comment_order_from_db(post_id)
        await cache_comment_order(post_id, comment_order)
    return comment_order


async def resolve_user_id_to_name(user_id: int) -> str:
    return f'{user_id}'


async def replace_user_id_with_username(comment_contents: Dict[str, CommentInfoCache]) -> Dict[str, CommentInfoResponse]:
    tasks = []
    for key in comment_contents:
        tasks.append(asyncio.create_task(resolve_user_id_to_name(comment_contents[key].author_id)))

    usernames = await asyncio.gather(*tasks)

    comment_contents_response = {}

    for key, username in zip(comment_contents, usernames):
        comment_contents_response[key] = CommentInfoResponse(username=username, **comment_contents[key].dict())

    return comment_contents_response


async def load_and_cache_comment_content(post_id: int) -> Dict[str, CommentInfoResponse]:
    comment_contents, ok = await get_cached_comment_contents(post_id)
    if not ok:
        db_comment_contents = await get_comment_contents_from_db(post_id)
        comment_contents = await cache_comment_contents(post_id, db_comment_contents)
    else:
        comment_contents = {x: CommentInfoCache(**comment_contents[x]) for x in comment_contents}

    comment_contents_response = await replace_user_id_with_username(comment_contents)

    return comment_contents_response
