import os
import sys
import datetime

myPath = os.path.dirname(os.path.abspath(__file__))
myPath = myPath.split('/tests')[0]
sys.path.insert(0, myPath)

import pytest
from redis import Redis
from dotenv import load_dotenv

load_dotenv(myPath + '/.env-local-pytests')

from app import app, db
from app.models import Sites, Posts, Comments, Users
from app.schemas.comments import CommentOrder
from tests.formatters_test_fixtures.comment_fixtures import reuseable_timestamp


@pytest.fixture
def client():
    # For this to work properly the DB needs to exist beforehand, so make sure to set the env
    # variables to a local testing db and run `alembic upgrade head` before the tests
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            yield client
            db.session.remove()


@pytest.fixture
def redis() -> None:
    redis = Redis(host=os.environ.get('REDIS_HOST'),
                  port=os.environ.get('REDIS_PORT'),
                  db=os.environ.get('REDIS_DB'))
    yield redis
    redis.flushdb()


@pytest.fixture
def clean_up_db() -> None:
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()


@pytest.fixture
def sample_site() -> Sites:
    site = Sites(name='testsite',
                 created_at=datetime.datetime.utcnow(),
                 is_deleted=False)
    return site


@pytest.fixture
def sample_user() -> Users:
    user = Users(user_name='testuser',
                 email='test@test.test',
                 created_at=datetime.datetime.utcnow())
    user.hash_password('testpassword')
    return user


@pytest.fixture
def sample_post() -> Posts:
    post = Posts(title='Test post title',
                 content="Some post content",
                 created_at=datetime.datetime.utcnow(),
                 is_deleted=False,
                 author_id=1,
                 site_id=1)
    return post


@pytest.fixture
def sample_comment(reuseable_timestamp) -> Comments:
    comment = Comments(content='This is some sample content',
                       created_at=reuseable_timestamp,
                       author_id=1,
                       post_id=1,
                       parent_comment_id=0,
                       is_deleted=False)
    return comment
