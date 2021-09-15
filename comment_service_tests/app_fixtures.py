import asyncio
import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from dotenv import load_dotenv
myPath = myPath.split('/comment_service_tests')[0]
load_dotenv(myPath+'/.env-local-pytests')

import pytest
from databases import Database
from fastapi.testclient import TestClient

from comment_service.main import get_application, db, redis_cache


# Override when eventloop closes to not get Event loop closed issue when re-using redis_cache object
@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client() -> TestClient:
    app = get_application()
    test_client = TestClient(app)
    yield test_client


@pytest.fixture
async def db_client() -> Database:
    await redis_cache.redis.flushdb()
    await db.connect()
    await db.execute('ALTER SEQUENCE comments_id_seq RESTART WITH 1')
    yield db
    await db.disconnect()
