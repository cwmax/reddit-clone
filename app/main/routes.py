import datetime
from typing import Optional

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


def create_and_submit_comment(content, parent_comment_id, post):
    comment = Comments(content=content,
                       created_at=datetime.datetime.utcnow(),
                       author_id=current_user.id,
                       post_id=post.id,
                       parent_comment_id=parent_comment_id,
                       is_deleted=False)
    return add_to_session_and_submit(comment, 'submit_comment')


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


def get_comments_with_user_information_for_posts(post: Posts) -> Optional[list]:
    res = db.session.query(Comments, Users).filter_by(post_id=post.id) \
        .join(Users, Users.id == Comments.author_id) \
        .order_by(Comments.parent_comment_id.asc(), Comments.created_at.asc()) \
        .all()
    return res


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
def post_page(site_name: str, post_id: int):
    post, site = get_post_and_site(post_id, site_name)
    if not validate_post_and_site(post, site):
        return redirect(url_for('main.site', site_name=site.name))
    # this will be optimized from join instead to cache lookup
    comments_and_users = get_comments_with_user_information_for_posts(post)

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
        post, ok = create_and_submit_post(site, form)
        if ok:
            redirect_url = url_for('main.post_page', site_name=site.name, post_id=post.id)
            return redirect(redirect_url)

    return render_template('main/submit_post.html', form=form, site_name=site_name)


@bp.route('/s/<site_name>/<post_id>/submit_comment', methods=['GET', 'POST'])
def submit_comment(site_name, post_id):
    post, site = get_post_and_site(post_id, site_name)
    if not validate_post_and_site(post, site):
        return redirect(url_for('main.site', site_name=site.name))

    parent_comment_id = request.args.get('parent_comment', 0)

    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data
        redirect_url = url_for('main.post_page', site_name=site_name, post_id=post.id)
        if create_and_submit_comment(content, parent_comment_id, post):
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


# TODO, make sure to use one redis connection over several commands, apparently it's a best practice