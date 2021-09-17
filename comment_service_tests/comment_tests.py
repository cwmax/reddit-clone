import asyncio
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from dotenv import load_dotenv

myPath = myPath.split('/comment_service_tests')[0]
load_dotenv(myPath + '/.env-local-pytests')

import pytest

from app_fixtures import client, event_loop, db_client
from comment_service.db.crud.comments import (insert_comment_into_db, get_comment_from_db_with_comment_id,
                                              get_comment_from_db_with_comment_info, insert_and_cache_comment,
                                              get_comment_order_from_db, insert_or_update_vote_in_db)
from comment_service_tests.fixtures.comment_fixtures import (sample_comment, reuseable_timestamp,
                                                             sample_comment_response, sample_comment_2,
                                                             reuseable_timestamp_2, sample_comment_order,
                                                             sample_comment_content_response, sample_comment_contents,
                                                             sample_comment_indent_levels,
                                                             sample_comment_indent_levels_layered,
                                                             sample_comment_3, sample_upvote, sample_downvote,
                                                             sample_comment_order_multiple, sample_comment_order_multiple_3)
from comment_service.core import get_redis_cache
from comment_service.main import db
from comment_service.schemas.comments import CommentInfo, CommentInfoCache
from comment_service.db.redis_cache.comments import (cache_comment, get_comment_info_cache_name_and_key,
                                                     get_cached_comment_order, cache_comment_order,
                                                     set_user_vote_in_cache,
                                                     get_comment_vote_cache_value,)
from comment_service.db.models.comments import comments, comment_events
from comment_service.db.comments import (load_and_cache_comment_order, load_and_cache_comment_content,
                                         get_cached_comment_contents, check_user_vote_exists_cache_and_db,
                                         determine_vote_change_value, set_or_update_comment_vote_in_cache)
from comment_service.utils.comments import get_comment_indent_level

redis_cache = get_redis_cache()


@pytest.mark.asyncio
async def test_insert_comment_into_db(db_client, sample_comment):
    async with db.transaction(force_rollback=True):
        comment_id = await insert_comment_into_db(sample_comment)
        res = await db.fetch_one("SELECT * FROM comments WHERE id=:comment_id",
                                 {'comment_id': comment_id})
    assert res is not None
    assert sample_comment == CommentInfo(**dict(zip(res._mapping.keys(), res._mapping.values())))


@pytest.mark.asyncio
async def test_get_comment_from_db_with_comment_id(db_client, sample_comment, sample_comment_response):
    async with db.transaction(force_rollback=True):
        comment_id = await insert_comment_into_db(sample_comment)
        comment = await get_comment_from_db_with_comment_id(comment_id=comment_id)
    assert sample_comment_response == comment


@pytest.mark.asyncio
async def test_get_comment_from_db_with_comment_info(db_client, sample_comment, sample_comment_response):
    async with db.transaction(force_rollback=True):
        await db.execute('ALTER SEQUENCE comments_id_seq RESTART WITH 1')
        await insert_comment_into_db(sample_comment)
        comment = await get_comment_from_db_with_comment_info(sample_comment)
    assert sample_comment_response == comment


@pytest.mark.asyncio
async def test_cache_comment(sample_comment_response):
    await cache_comment(sample_comment_response)
    name, key = get_comment_info_cache_name_and_key(sample_comment_response.post_id, sample_comment_response.id)
    cache_response = await redis_cache.hget(name, key)
    comment_info_cached_response = CommentInfoCache(**cache_response)

    await redis_cache.redis.close()

    assert comment_info_cached_response == CommentInfoCache(**sample_comment_response.dict())


@pytest.mark.asyncio
async def test_insert_and_cache_comment(db_client, sample_comment):
    async with db.transaction(force_rollback=True):
        comment_id = await insert_and_cache_comment(sample_comment)

    name, key = get_comment_info_cache_name_and_key(sample_comment.post_id, comment_id)
    cache_response = await redis_cache.hget(name, key)

    comment_info_cached_response = CommentInfoCache(**cache_response)

    await redis_cache.redis.close()

    assert comment_info_cached_response == CommentInfoCache(**sample_comment.dict())


@pytest.mark.asyncio
async def test_comments_model_insert_query(db_client, sample_comment):
    async with db.transaction(force_rollback=True):
        query = comments.insert()
        await db.execute(query=query, values=sample_comment.dict())
        query = comments.select()
        row = await db.fetch_one(query=query)

    assert row is not None


@pytest.mark.asyncio
async def test_get_cached_comment_order_empty(sample_comment):
    comment_order, ok = await get_cached_comment_order(sample_comment.post_id)
    assert ok is False
    assert comment_order is None


@pytest.mark.asyncio
async def test_get_cached_comment_order_not_empty(db_client, sample_comment, sample_comment_2, sample_comment_order):
    query = comments.insert()

    async with db.transaction(force_rollback=True):
        await db.execute_many(query=query, values=[sample_comment.dict(), sample_comment_2.dict()])
        comment_order = await get_comment_order_from_db(sample_comment.post_id)

    await cache_comment_order(sample_comment.post_id, comment_order)
    comment_order, ok = await get_cached_comment_order(sample_comment.post_id)
    assert ok is True
    assert comment_order == sample_comment_order


@pytest.mark.asyncio
async def test_load_and_cache_comment_order(db_client, sample_comment, sample_comment_2, sample_comment_order):
    query = comments.insert()
    async with db.transaction(force_rollback=True):
        await db.execute_many(query=query, values=[sample_comment.dict(), sample_comment_2.dict()])

        comment_order = await load_and_cache_comment_order(sample_comment.post_id)

        assert comment_order == sample_comment_order

        comment_order, ok = await get_cached_comment_order(sample_comment.post_id)
        assert ok is True
        assert comment_order == sample_comment_order


@pytest.mark.asyncio
async def test_get_cached_comment_contents_empty(db_client, sample_comment):
    comment_contents, ok = await get_cached_comment_contents(sample_comment.post_id, comment_id=0, comment_order=[])
    assert ok is False
    assert comment_contents is None


@pytest.mark.asyncio
async def test_load_and_cache_comment_content_empty(db_client, sample_comment):
    async with db.transaction(force_rollback=True):
        comment_contents = await load_and_cache_comment_content(sample_comment.post_id, 0, [])

        assert comment_contents == {}

        comment_contents, ok = await get_cached_comment_contents(sample_comment.post_id)
        assert ok is False
        assert comment_contents is None


@pytest.mark.asyncio
async def test_load_and_cache_comment_content(db_client, sample_comment, sample_comment_2, sample_comment_contents,
                                              sample_comment_content_response, sample_comment_order_multiple):
    query = comments.insert()

    async with db.transaction(force_rollback=True):
        await db.execute_many(query=query, values=[sample_comment.dict(), sample_comment_2.dict()])

        comment_contents = await load_and_cache_comment_content(sample_comment.post_id, 0, sample_comment_order_multiple)
        assert comment_contents == sample_comment_content_response

        comment_contents, ok = await get_cached_comment_contents(sample_comment.post_id, 0, sample_comment_order_multiple)
        assert ok is True
        assert comment_contents == sample_comment_contents


@pytest.mark.asyncio
async def test_get_comment_indent_level_empty(db_client, sample_comment):
    async with db.transaction(force_rollback=True):
        comment_contents = await load_and_cache_comment_content(sample_comment.post_id, 0, [])
        comment_indent_levels = get_comment_indent_level(comment_contents)
        assert comment_indent_levels == {'0': 0}


@pytest.mark.asyncio
async def test_get_comment_indent_level(db_client, sample_comment, sample_comment_2, sample_comment_indent_levels,
                                        sample_comment_order_multiple):
    query = comments.insert()

    async with db.transaction(force_rollback=True):
        await db.execute_many(query=query, values=[sample_comment.dict(), sample_comment_2.dict()])

        comment_contents = await load_and_cache_comment_content(sample_comment.post_id, 0, sample_comment_order_multiple)
        comment_indent_levels = get_comment_indent_level(comment_contents)
        assert comment_indent_levels == sample_comment_indent_levels


@pytest.mark.asyncio
async def test_get_comment_indent_level_layered(db_client, sample_comment, sample_comment_2, sample_comment_3,
                                                sample_comment_indent_levels_layered, sample_comment_order_multiple_3):
    query = comments.insert()

    async with db.transaction(force_rollback=True):
        await db.execute_many(query=query, values=[sample_comment.dict(), sample_comment_2.dict(),
                                                   sample_comment_3.dict()])

        comment_contents = await load_and_cache_comment_content(sample_comment.post_id, 0, sample_comment_order_multiple_3)
        comment_indent_levels = get_comment_indent_level(comment_contents)
        assert comment_indent_levels == sample_comment_indent_levels_layered


@pytest.mark.asyncio
async def test_check_vote_exists_or_changed(db_client, sample_upvote):
    comment_id = 1
    vote_value = await check_user_vote_exists_cache_and_db(sample_upvote.user_id, comment_id,
                                                                             sample_upvote.post_id)

    assert vote_value == 0


@pytest.mark.asyncio
async def test_determine_vote_no_change_value(db_client, sample_upvote):
    current_user_vote = 1
    vote_change_val = determine_vote_change_value(sample_upvote, current_user_vote)
    assert vote_change_val == 0


@pytest.mark.asyncio
async def test_determine_vote_change_value(db_client, sample_upvote):
    current_user_vote = 0
    vote_change_val = determine_vote_change_value(sample_upvote, current_user_vote)
    assert vote_change_val == 1


@pytest.mark.asyncio
async def test_determine_vote_down_to_upvote_change_value(db_client, sample_upvote):
    current_user_vote = -1
    vote_change_val = determine_vote_change_value(sample_upvote, current_user_vote)
    assert vote_change_val == 2


@pytest.mark.asyncio
async def test_determine_vote_up_to_downvote_change_value(db_client, sample_downvote):
    current_user_vote = 1
    vote_change_val = determine_vote_change_value(sample_downvote, current_user_vote)
    assert vote_change_val == -2


@pytest.mark.asyncio
async def test_check_vote_changed_and_insert_to_db(db_client, sample_comment, sample_upvote):
    async with db.transaction(force_rollback=True):
        comment_id = 1
        current_user_vote = await check_user_vote_exists_cache_and_db(sample_upvote.user_id, comment_id,
                                                                                 sample_upvote.post_id)

        assert current_user_vote == 0
        query = comments.insert()
        vote_change_val = determine_vote_change_value(sample_upvote, current_user_vote)

        await db.execute(query=query, values=sample_comment.dict())
        if vote_change_val != 0:
            await insert_or_update_vote_in_db(current_user_vote, sample_upvote, comment_id)
        query = comment_events.select()
        res = await db.fetch_all(query)

    assert len(res) == 1
    record = dict(zip(res[0]._mapping.keys(), res[0]._mapping.values()))

    assert record['user_id'] == 1
    assert record['event_value'] == 'upvote'
    assert record['event_name'] == 'vote'

@pytest.mark.asyncio
async def test_check_vote_changed_and_update_in_db(db_client, sample_upvote, sample_comment, sample_downvote):
    async with db.transaction(force_rollback=True):
        comment_id = 1
        current_user_vote = await check_user_vote_exists_cache_and_db(sample_upvote.user_id, comment_id,
                                                                      sample_upvote.post_id)

        assert current_user_vote == 0
        vote_change_val = determine_vote_change_value(sample_upvote, current_user_vote)

        cache_comment_vote_value = await get_comment_vote_cache_value(sample_upvote.post_id, comment_id)
        assert cache_comment_vote_value is None

        if vote_change_val != 0:
            await db.execute(query=comments.insert(), values=sample_comment.dict())
            await insert_or_update_vote_in_db(current_user_vote, sample_upvote, comment_id)

        await set_user_vote_in_cache(sample_upvote, comment_id)
        await set_or_update_comment_vote_in_cache(vote_change_val, comment_id, sample_upvote.post_id)

        cache_comment_vote_value = await get_comment_vote_cache_value(sample_upvote.post_id, comment_id)
        assert cache_comment_vote_value == 1

        current_user_vote = await check_user_vote_exists_cache_and_db(sample_downvote.user_id, comment_id,
                                                                      sample_downvote.post_id)
        vote_change_val = determine_vote_change_value(sample_downvote, current_user_vote)

        assert current_user_vote == 1
        assert vote_change_val == -2

        if vote_change_val != 0:
            await insert_or_update_vote_in_db(current_user_vote, sample_downvote, comment_id)
            res = await db.fetch_all(query=comment_events.select())

        record = dict(zip(res[0]._mapping.keys(), res[0]._mapping.values()))

        assert len(res) == 1
        assert record['user_id'] == 1
        assert record['event_value'] == 'downvote'
        assert record['event_name'] == 'vote'

        await set_user_vote_in_cache(sample_upvote, comment_id)
        await set_or_update_comment_vote_in_cache(vote_change_val, comment_id, sample_upvote.post_id)

        cache_comment_vote_value = await get_comment_vote_cache_value(sample_upvote.post_id, comment_id)
        assert cache_comment_vote_value == -1

    # @pytest.mark.asyncio
    # async def test_upvote_then_downvote(sample_upvote, sample_downvote):
    #     vote_value, exists = await check_vote_exists_or_changed(sample_upvote)
    #
    #     assert exists is False
    #     assert vote_value == 1
    #
    #     await update_vote_in_cache(sample_upvote, vote_value)
    #     vote_value, exists = await check_vote_exists_or_changed(sample_downvote)
    #
    #     assert exists is True
    #     assert vote_value is -2
    #     await update_vote_in_cache(sample_downvote, vote_value)

