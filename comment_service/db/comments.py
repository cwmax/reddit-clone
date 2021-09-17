from typing import List, Dict, Tuple
import asyncio

from comment_service.schemas.comments import CommentOrder, CommentInfoCache, CommentInfoResponse, CommentVote
from comment_service.db.redis_cache.comments import (get_cached_comment_order, cache_comment_order,
                                                     get_cached_comment_contents, cache_comment_contents,
                                                     check_comment_votes_exists, set_comment_vote_in_cache,
                                                     check_vote_exists_cache, update_comment_vote_in_cache,
                                                     check_cached_comment_votes_exists, get_comment_votes_from_cache,
                                                     update_comment_votes_in_cache)
from comment_service.db.crud.comments import (get_comment_order_from_db, get_comment_contents_from_db,
                                              fetch_comment_value_from_db, get_comment_vote_from_db,
                                              get_comment_votes_from_db)
from comment_service.db.utils.vote import convert_user_vote_to_value


def determine_vote_change_value(vote: CommentVote, redis_value: int) -> int:
    change_value = 0
    if vote.vote == 'upvote':
        if redis_value == -1:
            change_value = 2
        elif redis_value == 0:
            change_value = 1
        elif redis_value == 1:
            change_value = 0
    elif vote.vote == 'downvote':
        if redis_value == 1:
            change_value = -2
        elif redis_value == 0:
            change_value = 1
        elif redis_value == 1:
            change_value = 0

    return change_value


async def load_and_cache_comment_order(post_id: int) -> List[CommentOrder]:
    comment_order, ok = await get_cached_comment_order(post_id)
    if not ok:
        comment_order = await get_comment_order_from_db(post_id)
        await cache_comment_order(post_id, comment_order)
    return comment_order


async def resolve_user_id_to_name(user_id: int) -> str:
    return f'{user_id}'


async def replace_user_id_with_username(comment_contents: Dict[str, CommentInfoResponse]) -> Dict[
    str, CommentInfoResponse]:
    tasks = []
    for key in comment_contents:
        tasks.append(asyncio.create_task(resolve_user_id_to_name(comment_contents[key].username)))

    usernames = await asyncio.gather(*tasks)

    for key, username in zip(comment_contents, usernames):
        comment_contents[key].username = username

    return comment_contents


async def join_comment_content_and_votes(comment_votes: Dict[str, int],
                                         comment_contents: Dict[str, CommentInfoCache],
                                         user_id: int) -> \
        Dict[str, CommentInfoResponse]:
    comment_contents_response = {}
    tasks = []
    comment_ids = []
    for comment_id in comment_contents:
        comment_ids.append(comment_id)
        comment_vote = comment_votes.get(comment_id, 0)
        tasks.append(asyncio.create_task(check_user_vote_exists_cache_and_db(user_id=user_id,
                                                                             comment_id=int(comment_id),
                                                                             post_id=comment_contents[comment_id].post_id)))
        comment_contents_response[comment_id] = CommentInfoResponse(upvote_count=comment_vote,
                                                                    username=str(comment_contents[comment_id].author_id),
                                                                    **comment_contents[comment_id].dict())

    users_upvoted = await asyncio.gather(*tasks)
    for comment_id, user_upvoted in zip(comment_ids, users_upvoted):
        if user_upvoted == 1:
            user_upvoted = True
        elif user_upvoted == -1:
            user_upvoted = False
        elif user_upvoted == 0:
            user_upvoted = None
        comment_contents_response[comment_id].user_upvoted = user_upvoted

    return comment_contents_response


async def get_comment_votes(post_id: int) -> Dict[str, int]:
    exists = await check_cached_comment_votes_exists(post_id)
    if exists:
        comment_votes = await get_comment_votes_from_cache(post_id)
    else:
        comment_votes = await get_comment_votes_from_db(post_id)
        if len(comment_votes) > 0:
            await update_comment_votes_in_cache(post_id, comment_votes)
    return comment_votes


async def load_and_cache_comment_content(post_id: int, user_id: int, comment_order: List[CommentOrder]) \
        -> Dict[str, CommentInfoResponse]:
    comment_contents, ok = await get_cached_comment_contents(post_id, comment_order=comment_order)
    if not ok:
        db_comment_contents = await get_comment_contents_from_db(post_id)
        comment_contents = await cache_comment_contents(post_id, db_comment_contents)
    else:
        comment_contents = {x: CommentInfoCache(**comment_contents[x].dict()) for x in comment_contents}

    comment_votes = await get_comment_votes(post_id)

    comment_contents_response = await join_comment_content_and_votes(comment_votes, comment_contents, user_id)

    comment_contents_response = await replace_user_id_with_username(comment_contents_response)

    return comment_contents_response


async def get_user_vote_from_db(comment_id, user_id: int, post_id: int) -> None:
    res = await fetch_comment_value_from_db(comment_id, user_id)
    if res is not None:
        record = dict(zip(res._mapping.keys(), res._mapping.values()))
        vote = record.get('event_value')
    else:
        vote = ''

    vote_value = convert_user_vote_to_value(CommentVote(user_id=user_id,
                                                        post_id=post_id,
                                                        vote=vote))
    return vote_value


async def check_user_vote_exists_cache_and_db(user_id: int, comment_id: int, post_id: int) -> int:
    current_user_vote = await check_vote_exists_cache(user_id, comment_id)

    if current_user_vote is None:
        current_user_vote = await get_user_vote_from_db(comment_id, user_id, post_id)

    assert type(current_user_vote) == int
    return current_user_vote


async def set_comment_vote_in_cache_from_db(comment_id, post_id):

    comment_vote_val = await get_comment_vote_from_db(comment_id)
    await set_comment_vote_in_cache(comment_vote_val, comment_id, post_id)


async def set_or_update_comment_vote_in_cache(vote_change_value: int, comment_id: int, post_id: int) -> None:
    exists = await check_comment_votes_exists(post_id, comment_id)
    if exists:
        print('About to update comment value with:', vote_change_value)
        await update_comment_vote_in_cache(vote_change_value, comment_id, post_id)
    else:
        print('About to set comment value with:', vote_change_value)
        await set_comment_vote_in_cache_from_db(comment_id, post_id)
