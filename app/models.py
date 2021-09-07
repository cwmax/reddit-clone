from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


class Users(UserMixin, db.Model):
    __table__ = db.Model.metadata.tables['users']

    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


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
