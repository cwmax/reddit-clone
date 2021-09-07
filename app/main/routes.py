import datetime
from typing import Dict

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.main.forms import CreateSiteForm, CreatePostForm, CommentForm
from app.main import bp
from app.models import Sites, Posts, Comments, Users
from app.main.validators.site_validators import validate_site_name
from app.main.submit_helpers import add_to_session_and_submit
from app.main.validators.post_validators import validate_post_site_ids
from app.main.formatters.comment_formatters import format_comments
from app import db


def validate_new_site_name(site_name):
    if not validate_site_name(site_name):
        flash('Site name can only contain characters')
        return redirect(url_for('main.create_site'))

    if Sites.query.filter_by(name=site_name).first() is not None:
        flash('Site already exists')
        return redirect(url_for('main.create_site'))


def create_and_submit_site(site_name, redirect_url):
    site = Sites(name=site_name,
                 created_at=datetime.datetime.utcnow(),
                 is_deleted=False)

    if add_to_session_and_submit(site, 'submit_comment'):
        return redirect(redirect_url)


def create_and_submit_comment(content, parent_comment_id, post):
    comment = Comments(content=content,
                       created_at=datetime.datetime.utcnow(),
                       author_id=current_user.id,
                       post_id=post.id,
                       parent_comment_id=parent_comment_id,
                       is_deleted=False)
    return add_to_session_and_submit(comment, 'submit_comment')


def create_and_submit_post(site: Sites, form: CreatePostForm):
    post_title = form.title.data
    post_content = form.content.data
    post = Posts(title=post_title,
                 content=post_content,
                 created_at=datetime.datetime.utcnow(),
                 is_deleted=False,
                 author_id=current_user.id,
                 site_id=site.id)
    redirect_url = url_for('main.post', site_name=site.name, post_id=post.id)
    if add_to_session_and_submit(post, 'submit_post'):
        return redirect(redirect_url)


def get_post_and_site(post_id: str, site_name: str) -> (Posts, Sites):
    post_id = int(post_id)
    post = Posts.query.get(post_id)
    site = Sites.query.filter_by(name=site_name).first()

    return post, site


def validate_post_and_site(post: Posts, site: Sites):
    msg, ok = validate_post_site_ids(post, site)
    if not ok:
        flash(msg)
        return redirect(url_for('main.site', site_name=site.name))



@bp.route('/')
@bp.route('/home')
def home():
    return render_template('main/home.html')


@bp.route('/s/<site_name>', methods=['GET', 'POST'])
def subsite(site_name: str):
    site = Sites.query.filter_by(name=site_name)
    if site is None:
        flash(f"site {site_name} doesn't exist")
        return redirect(url_for('main.home'))

    return render_template('main/subsite.html', site_name=site_name)


@bp.route('/s/<site_name>/<post_id>', methods=['GET', 'POST'])
def post(site_name: str, post_id: int):
    post, site = get_post_and_site(post_id, site_name)
    validate_post_and_site(post, site)
    # this will be optimized from join instead to cache lookup
    comments_and_users = db.session.query(Comments, Users).filter_by(post_id=post.id)\
        .join(Users, Users.id == Comments.author_id)\
        .order_by(Comments.parent_comment_id.asc(), Comments.created_at.asc())\
        .all()

    comment_order, comment_contents, comment_indent_level = format_comments(comments_and_users)
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
        create_and_submit_post(site, form)

    return render_template('main/submit_post.html', form=form, site_name=site_name)


@bp.route('/s/<site_name>/<post_id>/submit_comment', methods=['GET', 'POST'])
def submit_comment(site_name, post_id):
    post, site = get_post_and_site(post_id, site_name)
    validate_post_and_site(post, site)
    parent_comment_id = request.args.get('parent_comment', 0)
    print('parent_comment_id is:', parent_comment_id)
    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data
        redirect_url = url_for('main.post', site_name=site_name, post_id=post.id)
        if create_and_submit_comment(content, parent_comment_id, post):
            return redirect(redirect_url)

    return render_template('main/submit_comment.html', form=form, post_title=post.title)


@bp.route('/create-site', methods=['GET', 'POST'])
@login_required
def create_site():
    form = CreateSiteForm()
    if form.validate_on_submit():
        site_name = form.site_name.data.lower()
        validate_new_site_name(site_name)
        redirect_url = url_for('main.subsite', site_name=site_name)
        create_and_submit_site(site_name, redirect_url)

    return render_template('main/create_site.html', form=form)
