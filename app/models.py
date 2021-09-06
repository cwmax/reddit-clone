from flask_login import UserMixin

from app import db
from app import login


class Users(UserMixin, db.Model):
    __table__ = db.Model.metadata.tables['users']


class Comments(db.Model):
    __table__ = db.Model.metadata.tables['comments']


class Posts(db.Model):
    __table__ = db.Model.metadata.tables['posts']


class PostEvents(db.Model):
    __table__ = db.Model.metadata.tables['post_events']


class CommentEvents(db.Model):
    __table__ = db.Model.metadata.tables['comment_events']


class Sites(db.Model):
    __table__ = db.Model.metadata.tables['sites']


class UserSiteFollows(db.Model):
    __table__ = db.Model.metadata.tables['user_site_follows']


class UserSiteAdmins(db.Model):
    __table__ = db.Model.metadata.tables['user_site_admins']


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))
