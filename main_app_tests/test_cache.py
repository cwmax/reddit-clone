import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from dotenv import load_dotenv

myPath = myPath.split('/main_app_tests')[0]
load_dotenv(myPath + '/.env-local-pytests')

from app.main.routes import add_to_session_and_submit
from app import db
from app.main.redis_cache_helpers import (add_new_comment_to_comment_cache, check_cache_exists_and_if_decomp_deser,
                                          get_comment_order_cache_name, update_comment_vote_cache)
from app.main.formatters.comment_formatters import get_comment_final_upvote_count
from app_test_fixtures.app_test_fixtures import (redis, clean_up_db, sample_site,
                                                 sample_post, sample_user, sample_comment)
from formatters_test_fixtures.comment_fixtures import (sample_comment_order, sample_comment_upvote,
                                                       sample_comment_downvote, reuseable_timestamp)


def add_site_user_post_comment(sample_site, sample_user, sample_post, sample_comment):

    add_to_session_and_submit(sample_site, 'submit_site')
    add_to_session_and_submit(sample_user, 'submit_user')
    add_to_session_and_submit(sample_post, 'submit_post')
    add_to_session_and_submit(sample_comment, 'submit_comment')


def test_add_new_comment_to_comment_cache(redis, clean_up_db, sample_site, sample_post, sample_user, sample_comment,
                                          sample_comment_order):
    comment_order_cache_name = get_comment_order_cache_name(post_id=1)
    add_site_user_post_comment(sample_site, sample_user, sample_post, sample_comment)
    add_new_comment_to_comment_cache(sample_post, sample_comment)
    data, exists = check_cache_exists_and_if_decomp_deser(comment_order_cache_name)
    assert exists is True
    assert data == sample_comment_order


def test_comment_data_taken_from_cache_not_db_when_available(redis, clean_up_db, sample_site, sample_post, sample_user,
                                                             sample_comment,
                                                             sample_comment_order):
    comment_order_cache_name = get_comment_order_cache_name(post_id=1)
    add_site_user_post_comment(sample_site, sample_user, sample_post, sample_comment)
    add_new_comment_to_comment_cache(sample_post, sample_comment)
    # This wouldn't happen in the app, since we mark it as deleted rather than actually deleting it
    # However, we do this to make sure we get the data from cache first if it exists before going to DB
    with db.engine.connect() as conn:
        conn.execute('DELETE FROM comments')
        res = conn.execute('SELECT * from comments').fetchall()

    assert len(res) == 0
    data, exists = check_cache_exists_and_if_decomp_deser(comment_order_cache_name)
    assert exists is True
    assert data == sample_comment_order


def test_comment_data_not_taken_from_when_not_available(redis, clean_up_db, sample_site, sample_post, sample_user,
                                                             sample_comment,
                                                             sample_comment_order):
    comment_order_cache_name = get_comment_order_cache_name(post_id=1)
    add_site_user_post_comment(sample_site, sample_user, sample_post, sample_comment)
    data, exists = check_cache_exists_and_if_decomp_deser(comment_order_cache_name)
    with db.engine.connect() as conn:
        res = conn.execute('SELECT * from comments').fetchall()

    assert len(res) != 0
    assert exists is False
    assert data is None


def test_update_comment_upvote_cache(redis, clean_up_db, sample_site, sample_post, sample_user,
                                   sample_comment, sample_comment_upvote):
    add_site_user_post_comment(sample_site, sample_user, sample_post, sample_comment)
    add_to_session_and_submit(sample_comment_upvote, 'submit_comment_vote')

    incr_vl = 1 if sample_comment_upvote.event_value == 'upvote' else -1
    update_comment_vote_cache(sample_post.id, sample_comment.id, incr_vl)
    upvote_count = get_comment_final_upvote_count(sample_post.id, sample_comment.id)
    assert upvote_count == incr_vl


def test_update_comment_downvote_cache(redis, clean_up_db, sample_site, sample_post, sample_user,
                                   sample_comment, sample_comment_downvote):
    add_site_user_post_comment(sample_site, sample_user, sample_post, sample_comment)
    add_to_session_and_submit(sample_comment_downvote, 'submit_comment_vote')

    incr_vl = -1 if sample_comment_downvote.event_value == 'downvote' else 1
    update_comment_vote_cache(sample_post.id, sample_comment.id, incr_vl)
    upvote_count = get_comment_final_upvote_count(sample_post.id, sample_comment.id)
    assert upvote_count == incr_vl
