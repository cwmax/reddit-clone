import datetime
import os
from typing import List, Tuple, Optional, Dict
import pickle
import snappy

from sqlalchemy import text

from app import app, db, redis
from app.models import Comments, Users, Posts
from app.schemas.comments import CommentUserAndContent, CommentOrder


def get_post_comment_content_and_order_from_db(post: Posts) -> (Optional[List[tuple]], Optional[List[tuple]]):
    res = db.session.query(Comments, Users).filter_by(post_id=post.id) \
        .join(Users, Users.id == Comments.author_id) \
        .order_by(Comments.parent_comment_id.asc(), Comments.created_at.asc()) \
        .all()
    return res


def serialize_and_compress_data(data):
    pickled_data = pickle.dumps(data)
    compressed_data = snappy.compress(pickled_data)
    return compressed_data


def deserialize_and_decompress_data(data):
    decompressed_data = snappy.decompress(data)
    depickled_data = pickle.loads(decompressed_data)
    return depickled_data


def cache_comment_order(name: str, post_comment_user_information: Tuple[tuple, tuple]) -> List[CommentOrder]:
    order_information = [CommentOrder(comment_id=c.id,
                                      created_at=c.created_at) for c, _ in post_comment_user_information]
    # Assumes only python code uses this data
    snappy_compressed_data = serialize_and_compress_data(order_information)
    redis.setex(name=name,
                time=int(os.environ.get('REDIS_CACHE_TTL_MS', 24 * 60 * 60 * 1000)),
                value=snappy_compressed_data)
    return order_information


def cache_comment_user_and_content_information(name: str, post_comment_user_information: Tuple[tuple, tuple]) -> \
        Dict[int, CommentUserAndContent]:
    comment_user_and_content = {c.id: CommentUserAndContent(username=u.user_name,
                                                            content=c.content,
                                                            parent_comment_id=c.parent_comment_id)
                                for c, u in post_comment_user_information}
    # Assumes only python code uses this data
    snappy_compressed_data = {key: serialize_and_compress_data(comment_user_and_content[key])
                              for key in comment_user_and_content}

    redis.hset(name, mapping=snappy_compressed_data)
    redis.expire(name, time=int(os.environ.get('REDIS_CACHE_TTL_MS', 24 * 60 * 60 * 1000)))
    return comment_user_and_content


def get_comments_order_for_posts(post: Posts) -> List[CommentOrder]:
    comment_order_cache_name = f'{post.id}_c_o'
    if redis.exists(comment_order_cache_name):
        compressed_data = redis.get(comment_order_cache_name)
        return deserialize_and_decompress_data(compressed_data)
    else:
        return get_post_comment_order_and_update_cache_with_comment_information(post)


def get_comments_user_and_content_for_posts_from_cache(name: str, comment_order: List[CommentUserAndContent]) \
        -> List[CommentUserAndContent]:
    if len(comment_order) == 0:
        return []
    keys = [i.comment_id for i in comment_order]
    ser_and_comp_comment_user_and_content = redis.hmget(name, keys=keys)
    redis.expire(name, time=int(os.environ.get('REDIS_CACHE_TTL_MS', 24 * 60 * 60 * 1000)))

    deserialized_and_decompressed_data = []
    for v in ser_and_comp_comment_user_and_content:
        deserialized_and_decompressed_data.append(deserialize_and_decompress_data(v))
    return deserialized_and_decompressed_data


def get_username_for_user_id(user_id):
    return db.session.query(Users.user_name).filter_by(id=int(user_id)).first()


def add_new_comment_to_comment_cache(post: Posts, comment: Comments):
    comment_order_cache_name = f'{post.id}_c_o'
    comment_order = []
    if redis.exists(comment_order_cache_name):
        compressed_data = redis.get(comment_order_cache_name)
        comment_order = deserialize_and_decompress_data(compressed_data)
    comment_order.append(CommentOrder(comment_id=comment.id,
                                      created_at=comment.created_at))
    snappy_compressed_data = serialize_and_compress_data(comment_order)
    redis.setex(name=comment_order_cache_name,
                time=int(os.environ.get('REDIS_CACHE_TTL_MS', 24 * 60 * 60 * 1000)),
                value=snappy_compressed_data)

    comment_user_and_content_cache_name = f'{post.id}_u_c'
    key = comment.id
    # TODO: implement caching of user info
    user_name = get_username_for_user_id(comment.author_id)

    user_name = user_name[0] if user_name is not None else None

    data = CommentUserAndContent(username=user_name,
                                 content=comment.content,
                                 parent_comment_id=comment.parent_comment_id)
    snappy_compressed_data = serialize_and_compress_data(data)

    redis.hset(comment_user_and_content_cache_name, key=key, value=snappy_compressed_data)
    redis.expire(comment_user_and_content_cache_name,
                 time=int(os.environ.get('REDIS_CACHE_TTL_MS', 24 * 60 * 60 * 1000)))


def get_post_comment_order_and_update_cache_with_comment_information(post: Posts) -> \
        List[CommentOrder]:
    """
    Gets comment order in asc order from DB and caches it. Also caches comment order, comment content.
    :param post:
    :return:
    """
    res = get_post_comment_content_and_order_from_db(post)
    if len(res) > 0:
        comment_order_cache_name = f'{post.id}_c_o'
        comment_order = cache_comment_order(comment_order_cache_name, res)
        comment_user_and_content_cache_name = f'{post.id}_u_c'
        cache_comment_user_and_content_information(comment_user_and_content_cache_name, res)
    else:
        comment_order = []
    return comment_order


def tally_final_upvotes_and_downvotes(res: List[Tuple[str, int]]):
    upvotes = 0
    downvotes = 0

    if res is None:
        return upvotes, downvotes
    if len(res) == 0:
        return upvotes, downvotes

    for vote, value in res:
        if vote == 'upvote':
            upvotes += value
        elif vote == 'downvote':
            downvotes += value

    return upvotes, downvotes


def get_comment_final_upvote_count_from_db(comment_id: int) -> int:
    vote_count_query = """SELECT event_value, count(*) as vote_count
        from comment_events
        where comment_id = :comment_id AND event_name = 'vote'
        group by event_value"""
    with db.engine.connect() as conn:
        res = conn.execute(text(vote_count_query), {'comment_id': comment_id}).fetchall()

    upvotes, downvotes = tally_final_upvotes_and_downvotes(res)

    return upvotes - downvotes


def insert_value_into_redis_from_db(name: str, key: str) -> int:
    current_vote_count = get_comment_final_upvote_count_from_db(int(key))
    redis.hsetnx(name, key, current_vote_count)
    redis.expire(name, time=int(os.environ.get('REDIS_CACHE_TTL_MS', 24 * 60 * 60 * 1000)))
    return current_vote_count


def update_value_in_redis(name: str, key: str, increment_value: int) -> None:
    try:
        redis.hincrby(name, key, increment_value)
    except Exception as e:
        app.logger.error(f"Encountered {e} in update_value_in_redis")


def update_comment_vote_cache(post_id: int, comment_id: int, increment_value: int) -> None:
    name = f'{post_id}'
    key = f'{comment_id}'
    if redis.hexists(name, key):
        update_value_in_redis(name, key, increment_value)
    else:
        insert_value_into_redis_from_db(name, key)
