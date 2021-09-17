from typing import List, Any, Dict
import datetime

from comment_service.main import db
from comment_service.schemas.comments import (CommentInfo, CommentModel, CommentOrder, CommentInfoDBResponse,
                                              CommentVote, CommentEvent)
from comment_service.db.redis_cache.comments import cache_comment
from comment_service.db.models.comments import comment_events, comments


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


def aggregate_single_comment_votes(res):
    final_score = 0
    for r in res:
        record = dict(zip(r._mapping.keys(), r._mapping.values()))
        event_value = record.get('event_value')
        count = record.get('count')
        if event_value == 'upvote':
            final_score += count
        elif event_value == 'downvote':
            final_score -= count

    return final_score


def aggregate_multiple_comment_votes(res) -> Dict[str, int]:
    final_score = {}
    for r in res:
        record = dict(zip(r._mapping.keys(), r._mapping.values()))
        comment_id = record.get('comment_id')
        final_score.setdefault(comment_id, 0)
        event_value = record.get('event_value')
        count = record.get('count')
        if event_value == 'upvote':
            final_score[comment_id] += count
        elif event_value == 'downvote':
            final_score[comment_id] -= count

    return final_score


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
            ORDER BY parent_comment_id ASC, created_at ASC"""

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


def prepare_vote_comment_event(vote: CommentVote, comment_id: int) -> CommentEvent:
    comment_event = CommentEvent(created_at=datetime.datetime.utcnow(),
                                 event_name='vote',
                                 user_id=vote.user_id,
                                 comment_id=comment_id,
                                 event_value=vote.vote)
    return comment_event


async def insert_or_update_vote_in_db(current_user_vote: int, vote: CommentVote, comment_id: int) -> None:
    updated = False if current_user_vote == 0 else True
    if not updated:
        await insert_vote_in_db(vote, comment_id)
    else:
        await update_vote_in_db(vote, comment_id)


async def insert_vote_in_db(vote: CommentVote, comment_id:int) -> None:
    query = comment_events.insert()
    comment_event = prepare_vote_comment_event(vote, comment_id)
    await db.execute(query=query, values=comment_event.dict())


async def update_vote_in_db(vote: CommentVote, comment_id:int) -> None:
    query = """UPDATE comment_events
    SET event_value=:vote
    WHERE user_id=:user_id AND comment_id=:comment_id AND event_name='vote'
    """

    await db.execute(query=query, values=dict(user_id=vote.user_id,
                                              comment_id=comment_id,
                                              vote=vote.vote))


async def fetch_comment_value_from_db(comment_id: int, user_id: int) -> int:
    query = """SELECT event_value 
    FROM comment_events
    WHERE comment_id=:comment_id AND event_name='vote' AND user_id=:user_id
    """

    res = await db.fetch_one(query=query, values=dict(comment_id=comment_id, user_id=user_id))

    return res


async def get_comment_vote_from_db(comment_id: int) -> int:
    query = """SELECT event_value, count(*) AS count
    FROM comment_events
    WHERE comment_id=:comment_id AND event_name='vote'
    GROUP BY event_value
    """

    res = await db.fetch_all(query=query, values={'comment_id': comment_id})
    final_votes = aggregate_single_comment_votes(res)
    return final_votes


async def get_comment_ids_for_post_from_db(post_id: int) -> List[int]:
    query = """SELECT *
    FROM comments
    WHERE post_id=:post_id"""
    res = await db.fetch_all(query=query, values={'post_id': post_id})
    comment_ids = []
    for record in res:
        comment_ids.append(record[0])

    return comment_ids


async def get_comment_votes_from_db(post_id: int) -> Dict[str, int]:
    query = """SELECT comment_id, event_value, count(*)
    FROM comment_events
    WHERE comment_id in {comment_ids} AND event_name='vote'
    GROUP BY comment_id, event_value"""

    comment_ids = await get_comment_ids_for_post_from_db(post_id)
    if len(comment_ids) > 0:
        res = await db.fetch_all(query=query.format(comment_ids=tuple(comment_ids)))

        comment_votes = aggregate_multiple_comment_votes(res)
    else:
        comment_votes = {}
    return comment_votes
