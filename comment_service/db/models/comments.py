import sqlalchemy


metadata = sqlalchemy.MetaData()

comments = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("content", sqlalchemy.String()),
    sqlalchemy.Column("author_id", sqlalchemy.Integer),
    sqlalchemy.Column("parent_comment_id", sqlalchemy.Integer),
    sqlalchemy.Column("post_id", sqlalchemy.Integer),
    sqlalchemy.Column("is_deleted", sqlalchemy.Boolean),
    sqlalchemy.Column("created_at", sqlalchemy.TIMESTAMP),
)
