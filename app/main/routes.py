import datetime
import os
from typing import Optional
import requests

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.main.forms import CreateSiteForm, CreatePostForm, CommentForm
from app.main import bp
from app.models import Sites, Posts, Comments, CommentEvents
from app.main.validators.site_validators import validate_site_name
from app.main.submit_helpers import add_to_session_and_submit
from app.main.validators.post_validators import validate_post_site_ids
from app.main.formatters.comment_formatters import format_comments, form_comment_and_user_information
from app import redis, app
from app.main.validators.comment_vote_validators import check_user_comment_existing_vote
from app.main.submit_helpers import submit_and_redirect_or_rollback
from app.main.redis_cache_helpers import (update_comment_vote_cache,
                                          get_comments_user_and_content_cache_name,
                                          get_comments_user_and_content_for_posts_from_cache,
                                          add_new_comment_to_comment_cache,
                                          get_comments_order_for_posts)
from app.schemas.comments import CommentOrder, CommentInfo


def validate_new_site_name(site_name):
    if not validate_site_name(site_name):
        flash('Site name can only contain characters')
        return False

    if Sites.query.filter_by(name=site_name).first() is not None:
        flash('Site already exists')
        return False
    return True


def create_and_submit_site(site_name):
    site = Sites(name=site_name,
                 created_at=datetime.datetime.utcnow(),
                 is_deleted=False)
    if add_to_session_and_submit(site, 'submit_site'):
        return True
    return False


def create_and_submit_new_vote(comment_id: int, event_value: str) -> bool:
    commentEvent = CommentEvents(created_at=datetime.datetime.utcnow(),
                                 event_name='vote',
                                 user_id=current_user.id,
                                 comment_id=comment_id,
                                 event_value=event_value)
    if add_to_session_and_submit(commentEvent, 'submit_comment_upvote'):
        return True
    return False


# TODO: add caching here
def create_and_submit_comment(content: str, parent_comment_id: id, post: Posts) -> (bool, Comments):
    comment = Comments(content=content,
                       created_at=datetime.datetime.utcnow(),
                       author_id=current_user.id,
                       post_id=post.id,
                       parent_comment_id=parent_comment_id,
                       is_deleted=False)
    return add_to_session_and_submit(comment, 'submit_comment'), comment


def create_and_submit_post(site: Sites, form: CreatePostForm) -> (Posts, bool):
    post_title = form.title.data
    post_content = form.content.data
    post = Posts(title=post_title,
                 content=post_content,
                 created_at=datetime.datetime.utcnow(),
                 is_deleted=False,
                 author_id=current_user.id,
                 site_id=site.id)
    if add_to_session_and_submit(post, 'submit_post'):
        return post, True
    return post, False


def get_post_and_site(post_id: str, site_name: str) -> (Posts, Sites):
    post_id = int(post_id)
    post = Posts.query.get(post_id)
    site = Sites.query.filter_by(name=site_name).first()

    return post, site


def validate_post_and_site(post: Posts, site: Sites) -> bool:
    msg, ok = validate_post_site_ids(post, site)
    if not ok:
        flash(msg)
        return False
    return True


def update_comment_event_value(res: CommentEvents, new_event_value: str) -> None:
    res.event_value = new_event_value
    res.created_at = datetime.datetime.utcnow()
    ok = submit_and_redirect_or_rollback(f'{new_event_value}_comment')
    if not ok:
        flash(f'Error encountered when switching to {new_event_value}')
    return


def update_comment_event_if_needed(comment_id: int, new_event_value: str) -> (bool, bool):
    res, has_existing_vote = check_user_comment_existing_vote(comment_id)
    if not has_existing_vote:
        ok = create_and_submit_new_vote(comment_id, new_event_value)
        if not ok:
            flash('Error encountered when upvoting comment')
            return False, False
        return True, False

    if res.event_value == new_event_value:
        return False, False

    update_comment_event_value(res, new_event_value)
    return True, True


def get_existing_values_if_exists(name: str, key: str) -> Optional[int]:
    if redis.hexists(name, key):
        return_val = int(redis.hget(name, key).decode())
        redis.expire(name, time=int(os.environ.get('REDIS_CACHE_TTL_MS', 24 * 60 * 60 * 1000)))
        return return_val

    return


@bp.route('/')
@bp.route('/home')
def home():
    sites = Sites.query.all()
    return render_template('main/home.html', sites=sites)


@bp.route('/s/<site_name>', methods=['GET', 'POST'])
def subsite(site_name: str):
    site = Sites.query.filter_by(name=site_name).first()
    if site is None:
        flash(f"site {site_name} doesn't exist")
        return redirect(url_for('main.home'))
    posts = Posts.query.all()
    return render_template('main/subsite.html', site_name=site_name, posts=posts)


@bp.route('/s/<site_name>/<post_id>', methods=['GET', 'POST'])
def post_page(site_name: str, post_id: int):
    post, site = get_post_and_site(post_id, site_name)
    if not validate_post_and_site(post, site):
        return redirect(url_for('main.site', site_name=site.name))

    user_authenticated = current_user.is_authenticated
    if user_authenticated:
        user_id = current_user.id
    else:
        user_id = 0
    app.logger.info(f'user_authenticated: {user_authenticated}')
    app.logger.info(f'user_id: {user_id}')

    response_value = requests.get(f'http://comment_service:8080/get-post-comments/{post_id}/{user_id}').json()
    comment_contents = response_value.get('comment_content')
    comment_contents = [CommentInfo(id=int(x), **comment_contents[x],
                                    user_comment_upvote=comment_contents[x].get('user_upvoted')) for x in
                        comment_contents]

    comment_order, comment_contents, comment_indent_level = format_comments(comment_contents, post_id,
                                                                            user_authenticated, user_id)
    return render_template('main/post.html', post_title=post.title, post_content=post.content,
                           site_name=site_name, post_id=post_id, comment_order=comment_order,
                           comment_contents=comment_contents, comment_indent_level=comment_indent_level)


@bp.route('/s/<site_name>/submit_post', methods=['GET', 'POST'])
def submit_post(site_name: str):
    site = Sites.query.filter_by(name=site_name).first()
    if site is None:
        flash(f"site {site_name} doesn't exist")
        return redirect(url_for('main.home'))

    form = CreatePostForm()
    if form.validate_on_submit():
        post, ok = create_and_submit_post(site, form)
        if ok:
            redirect_url = url_for('main.post_page', site_name=site.name, post_id=post.id)
            return redirect(redirect_url)

    return render_template('main/submit_post.html', form=form, site_name=site_name)


@bp.route('/s/<site_name>/<post_id>/submit_comment', methods=['GET', 'POST'])
@login_required
def submit_comment(site_name, post_id):
    post, site = get_post_and_site(post_id, site_name)
    if not validate_post_and_site(post, site):
        return redirect(url_for('main.site', site_name=site.name))

    parent_comment_id = request.args.get('parent_comment', 0)

    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data
        requests.post('http://comment_service:8080/submit-comment', json=dict(content=content,
                                                                              author_id=current_user.id,
                                                                              parent_comment_id=parent_comment_id,
                                                                              post_id=post_id))
        redirect_url = url_for('main.post_page', site_name=site_name, post_id=post.id)
        return redirect(redirect_url)

    return render_template('main/submit_comment.html', form=form, post_title=post.title)


@bp.route('/create-site', methods=['GET', 'POST'])
@login_required
def create_site():
    form = CreateSiteForm()
    if form.validate_on_submit():
        site_name = form.site_name.data.lower()
        if not validate_new_site_name(site_name):
            return redirect(url_for('main.create_site'))
        redirect_url = url_for('main.subsite', site_name=site_name)
        if create_and_submit_site(site_name):
            return redirect(redirect_url)

    return render_template('main/create_site.html', form=form)


@bp.get('/s/<site_name>/<post_id>/<comment_id>/upvote-comment')
@login_required
def upvote_comment(site_name: str, post_id: str, comment_id: str):
    requests.post(f'http://comment_service:8080/vote-comment/{comment_id}', json={'user_id': current_user.id,
                                                                                  'vote': 'upvote',
                                                                                  'post_id': post_id})
    redirect_url = url_for('main.post_page', site_name=site_name, post_id=post_id)

    return redirect(redirect_url)


@bp.get('/s/<site_name>/<post_id>/<comment_id>/downvote-comment')
@login_required
def downvote_comment(site_name: str, post_id: str, comment_id: str):
    requests.post(f'http://comment_service:8080/vote-comment/{comment_id}', json={'user_id': current_user.id,
                                                                                  'vote': 'downvote',
                                                                                  'post_id': post_id})
    redirect_url = url_for('main.post_page', site_name=site_name, post_id=post_id)

    return redirect(redirect_url)
