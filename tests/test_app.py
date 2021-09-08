import os
import sys
import datetime
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest
from dotenv import load_dotenv
load_dotenv('../.env-local-pytests')

from app import app, db
from app.main.routes import create_and_submit_site, add_to_session_and_submit, create_and_submit_comment
from app.models import Sites, Posts, Comments, Users
from app.auth.routes import create_and_submit_user


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
def sample_comment() -> Comments:
    comment = Comments(content='This is some sample content',
                       created_at=datetime.datetime.utcnow(),
                       author_id=1,
                       post_id=1,
                       parent_comment_id=0,
                       is_deleted=False)
    return comment


def test_empty_db(client):
    rv = client.get('/')
    rv_data = rv.data.decode('utf-8')
    assert 'SeenIt' in rv_data
    assert 'Create site' in rv_data


def test_create_site(clean_up_db):
    site_name = 'newTestSite'
    create_and_submit_site(site_name)
    resp = Sites.query.filter_by(name=site_name).first()

    assert resp is not None


def test_create_and_submit_user(clean_up_db, sample_user):
    create_and_submit_user(sample_user.user_name, sample_user.email, sample_user.password)
    resp = Users.query.filter_by(user_name=sample_user.user_name).first()

    assert resp is not None


def test_duplicate_create_site_succeeds(clean_up_db):
    site_name = 'newTestSite'
    create_and_submit_site(site_name)
    create_and_submit_site(site_name)
    resp = Sites.query.filter_by(name=site_name).all()

    assert resp is not None
    assert len(resp) == 1


def test_create_and_submit_post(clean_up_db, sample_site, sample_post, sample_user):
    add_to_session_and_submit(sample_site, 'submit_site')
    add_to_session_and_submit(sample_user, 'submit_user')
    add_to_session_and_submit(sample_post, 'submit_post')

    resp = Posts.query.filter_by(title='Test post title').first()
    assert resp is not None


def test_create_and_submit_post(clean_up_db, sample_site, sample_post, sample_user, sample_comment):
    add_to_session_and_submit(sample_site, 'submit_site')
    add_to_session_and_submit(sample_user, 'submit_user')
    add_to_session_and_submit(sample_post, 'submit_post')
    add_to_session_and_submit(sample_comment, 'submit_comment')

    resp = Comments.query.filter_by(content='This is some sample content').first()
    assert resp is not None

