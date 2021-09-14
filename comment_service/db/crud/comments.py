from typing import List

from comment_service.main import db
from comment_service.schemas.comments import CommentInfo, CommentModel


def get_comment_insert_query() -> str:
    insert_query = """INSERT INTO comments(created_at, author_id, content, post_id, parent_comment_id, is_deleted)
    VALUES (:created_at, :author_id, :content, :post_id, :parent_comment_id, :is_deleted)"""
    return insert_query


def get_comment_select_query_and_columns() -> (str, List[str]):
    select_columns = ['author_id', 'created_at', 'post_id', 'parent_comment_id']
    query = """SELECT * FROM comments WHERE author_id=:author_id AND created_at=:created_at AND 
    post_id=:post_id AND parent_comment_id=:parent_comment_id"""
    return query, select_columns


async def insert_comment_into_db(comment: CommentInfo) -> None:
    insert_query = get_comment_insert_query()
    await db.execute(query=insert_query, values=comment.dict())


async def get_comment_from_db_with_comment_id(comment_id: int) -> CommentModel:
    select_query = """SELECT * FROM comments where id=:comment_id"""
    res = await db.fetch_one(select_query, {'comment_id': comment_id})
    comment_info = CommentModel(**dict(zip(res._mapping.keys(), res._mapping.values())))
    return comment_info


async def get_comment_from_db_with_comment_info(comment: CommentInfo) -> CommentModel:
    query, select_columns = get_comment_select_query_and_columns()
    filter_values = {k: comment.dict()[k] for k in select_columns}
    res = await db.fetch_one(query, values=filter_values)
    comment_info = CommentModel(**dict(zip(res._mapping.keys(), res._mapping.values())))
    return comment_info
