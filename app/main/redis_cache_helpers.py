from typing import List, Tuple

from sqlalchemy import text

from app import app, db, redis


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