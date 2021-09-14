from comment_service.main import db


class Comments(db.Model):
    __table__ = db.Model.metadata.tables['comments']
