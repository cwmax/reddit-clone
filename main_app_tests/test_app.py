import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from dotenv import load_dotenv
myPath = myPath.split('/main_app_tests')[0]
load_dotenv(myPath+'/.env-local-pytests')

from app.main.routes import create_and_submit_site, add_to_session_and_submit
from app.models import Sites, Posts, Comments, Users
from app.auth.routes import create_and_submit_user
from app_test_fixtures.app_test_fixtures import (sample_comment, client, clean_up_db, sample_site,
                                                 sample_post, sample_user)
from formatters_test_fixtures.comment_fixtures import reuseable_timestamp



# General note on testing when you find bugs
# 1) write a test that demonstrates the bug
# 2) Make the fix
# 3) Have the test verify the fix
# 4) push changes

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


def test_create_and_submit_comment(clean_up_db, sample_site, sample_post, sample_user, sample_comment):
    add_to_session_and_submit(sample_site, 'submit_site')
    add_to_session_and_submit(sample_user, 'submit_user')
    add_to_session_and_submit(sample_post, 'submit_post')
    add_to_session_and_submit(sample_comment, 'submit_comment')

    resp = Comments.query.filter_by(content='This is some sample content').first()
    assert resp is not None
