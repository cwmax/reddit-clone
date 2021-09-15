from typing import List, Any

from comment_service.main import db
from comment_service.schemas.comments import CommentInfo, CommentModel, CommentOrder, CommentInfoDBResponse
from comment_service.db.redis_cache.comments import cache_comment


def get_comment_insert_query() -> str:
    insert_query = """INSERT INTO comments(created_at, author_id, content, post_id, parent_comment_id, is_deleted)
    VALUES (:created_at, :author_id, :content, :post_id, :parent_comment_id, :is_deleted)
    RETURNING id"""
    return insert_query


def get_comment_select_query_and_columns() -> (str, List[str]):
    select_columns = ['author_id', 'created_at', 'post_id', 'parent_comment_id']
    query = """SELECT * FROM comments WHERE author_id=:author_id AND created_at=:created_at AND 
    post_id=:post_id AND parent_comment_id=:parent_comment_id"""
    return query, select_columns


async def insert_comment_into_db(comment: CommentInfo) -> int:
    insert_query = get_comment_insert_query()
    comment_id = await db.execute(query=insert_query, values=comment.dict())
    return comment_id


async def insert_and_cache_comment(comment: CommentInfo) -> int:
    comment_id = await insert_comment_into_db(comment)
    comment_model = CommentModel(id=comment_id, **comment.dict())
    await cache_comment(comment_model)

    return comment_id


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


async def get_post_data_from_db_and_convert_to_type(query: str, values: dict, desired_type: Any) -> List[Any]:
    return_list = []
    res = await db.fetch_all(query=query, values=values)
    for record in res:
        record_dict = dict(zip(record._mapping.keys(), record._mapping.values()))
        return_list.append(desired_type(**record_dict))
    return return_list


async def get_comment_order_from_db(post_id: int) -> List[CommentOrder]:
    query = """SELECT id AS comment_id, created_at
            FROM comments
            WHERE post_id=:post_id
            ORDER BY created_at ASC"""

    values = {'post_id': post_id}
    return_list = await get_post_data_from_db_and_convert_to_type(query, values, CommentOrder)
    return return_list


async def get_comment_contents_from_db(post_id: int) -> List[CommentInfoDBResponse]:
    query = """SELECT id,
                    content,
                    author_id,
                    parent_comment_id,
                    post_id,
                    is_deleted
            FROM comments
            WHERE post_id=:post_id"""

    values = {'post_id': post_id}
    return_list = await get_post_data_from_db_and_convert_to_type(query, values, CommentInfoDBResponse)
    return return_list
