import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from dotenv import load_dotenv
myPath = myPath.split('/comment_service_tests')[0]
load_dotenv(myPath+'/.env-local-pytests')

import pytest

from app_fixtures import client
from comment_service.db.crud.comments import (insert_comment_into_db, get_comment_from_db_with_comment_id,
                                              get_comment_from_db_with_comment_info)
from comment_service_tests.fixtures.comment_fixtures import (sample_comment, reuseable_timestamp,
                                                             sample_comment_response)
from comment_service.main import db, redis_cache
from comment_service.schemas.comments import CommentInfo, CommentModel, CommentInfoCache
from comment_service.db.redis_cache.comments import cache_comment, get_comment_info_cache_name_and_key


@pytest.mark.asyncio
async def test_insert_comment_into_db(sample_comment):
    await db.connect()
    async with db.transaction(force_rollback=True):
        await insert_comment_into_db(sample_comment)
        res = await db.fetch_all("SELECT * FROM comments")
    assert len(res) > 0
    assert sample_comment == CommentInfo(**dict(zip(res[0]._mapping.keys(), res[0]._mapping.values())))

    await db.disconnect()


@pytest.mark.asyncio
async def test_get_comment_from_db_with_comment_id(sample_comment, sample_comment_response):
    await db.connect()

    async with db.transaction(force_rollback=True):
        await db.execute('ALTER SEQUENCE comments_id_seq RESTART WITH 1')
        await insert_comment_into_db(sample_comment)
        comment = await get_comment_from_db_with_comment_id(comment_id=1)
    assert sample_comment_response == comment

    await db.disconnect()


@pytest.mark.asyncio
async def test_get_comment_from_db_with_comment_info(sample_comment, sample_comment_response):
    await db.connect()

    async with db.transaction(force_rollback=True):
        await db.execute('ALTER SEQUENCE comments_id_seq RESTART WITH 1')
        await insert_comment_into_db(sample_comment)
        comment = await get_comment_from_db_with_comment_info(sample_comment)
    assert sample_comment_response == comment

    await db.disconnect()


@pytest.mark.asyncio
async def test_cache_comment(sample_comment_response):
    await cache_comment(sample_comment_response)
    name, key = get_comment_info_cache_name_and_key(sample_comment_response.post_id, sample_comment_response.id)
    cache_response = await redis_cache.hget(name, key)
    comment_info_cached_response = CommentInfoCache(**cache_response)
    assert comment_info_cached_response == CommentInfoCache(**sample_comment_response.dict())
