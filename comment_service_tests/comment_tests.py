import asyncio
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from dotenv import load_dotenv

myPath = myPath.split('/comment_service_tests')[0]
load_dotenv(myPath + '/.env-local-pytests')

import pytest

from app_fixtures import client
from comment_service.db.crud.comments import (insert_comment_into_db, get_comment_from_db_with_comment_id,
                                              get_comment_from_db_with_comment_info, insert_and_cache_comment,
                                              get_comment_order_from_db)
from comment_service_tests.fixtures.comment_fixtures import (sample_comment, reuseable_timestamp,
                                                             sample_comment_response, sample_comment_2,
                                                             reuseable_timestamp_2, sample_comment_order,
                                                             sample_comment_content_response, sample_comment_contents,
                                                             sample_comment_indent_levels)
from comment_service_tests.app_fixtures import event_loop, db_client
from comment_service.core import get_redis_cache
from comment_service.main import db
from comment_service.schemas.comments import CommentInfo, CommentModel, CommentInfoCache
from comment_service.db.redis_cache.comments import (cache_comment, get_comment_info_cache_name_and_key,
                                                     get_cached_comment_order, cache_comment_order)
from comment_service.db.models.comments import comments
from comment_service.db.comments import (load_and_cache_comment_order, load_and_cache_comment_content,
                                         get_cached_comment_contents)
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
    comment_contents, ok = await get_cached_comment_contents(sample_comment.post_id)
    assert ok is False
    assert comment_contents is None


@pytest.mark.asyncio
async def test_load_and_cache_comment_content_empty(db_client, sample_comment):
    async with db.transaction(force_rollback=True):

        comment_contents = await load_and_cache_comment_content(sample_comment.post_id)

        assert comment_contents == {}

        comment_contents, ok = await get_cached_comment_contents(sample_comment.post_id)
        assert ok is False
        assert comment_contents is None


@pytest.mark.asyncio
async def test_load_and_cache_comment_content(db_client, sample_comment, sample_comment_2, sample_comment_contents,
                                              sample_comment_content_response):
    query = comments.insert()

    async with db.transaction(force_rollback=True):
        await db.execute_many(query=query, values=[sample_comment.dict(), sample_comment_2.dict()])

        comment_contents = await load_and_cache_comment_content(sample_comment.post_id)
        assert comment_contents == sample_comment_content_response

        comment_contents, ok = await get_cached_comment_contents(sample_comment.post_id)
        assert ok is True
        assert comment_contents == sample_comment_contents


@pytest.mark.asyncio
async def test_get_comment_indent_level_empty(db_client, sample_comment):
    async with db.transaction(force_rollback=True):
        comment_contents = await load_and_cache_comment_content(sample_comment.post_id)
        comment_indent_levels = get_comment_indent_level(comment_contents)
        assert comment_indent_levels == {'0': 0}


@pytest.mark.asyncio
async def test_get_comment_indent_level(db_client, sample_comment, sample_comment_2, sample_comment_indent_levels):
    query = comments.insert()

    async with db.transaction(force_rollback=True):
        await db.execute_many(query=query, values=[sample_comment.dict(), sample_comment_2.dict()])

        comment_contents = await load_and_cache_comment_content(sample_comment.post_id)
        comment_indent_levels = get_comment_indent_level(comment_contents)
        assert comment_indent_levels == sample_comment_indent_levels

# get_comment_order(post_id)
#     comment_content = await get_comment_content(comment_order)
#     comment_indent_level = get_comment_indent_level(comment_cotent)

