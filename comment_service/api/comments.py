from fastapi import APIRouter
from comment_service.schemas.comments import CommentModel, CommentInfo, PostCommentResponse, CommentVote
from comment_service.db.crud.comments import (insert_and_cache_comment, get_comment_from_db_with_comment_id,
                                              insert_or_update_vote_in_db)
from comment_service.db.comments import (load_and_cache_comment_order, load_and_cache_comment_content,
                                         check_user_vote_exists_cache_and_db, determine_vote_change_value,
                                         set_or_update_comment_vote_in_cache)
from comment_service.utils.comments import get_comment_indent_level
from comment_service.db.redis_cache.comments import (set_user_vote_in_cache)

router = APIRouter()


@router.post('/submit-comment')
async def submit_comment(comment: CommentInfo):
    comment_id = await insert_and_cache_comment(comment)


@router.get('/get-comment/{comment_id}',
            response_model=CommentModel)
async def get_comment(comment_id: int):
    comment = await get_comment_from_db_with_comment_id(comment_id)
    return comment


@router.get('/get-post-comments/{post_id}/{user_id}',
            response_model=PostCommentResponse)
async def get_post_comments(post_id: int, user_id: int):
    comment_order = await load_and_cache_comment_order(post_id)
    comment_content = await load_and_cache_comment_content(post_id, user_id, comment_order)
    comment_indent_level = get_comment_indent_level(comment_content)

    post_comment_response = PostCommentResponse(comment_order=comment_order,
                                                comment_content=comment_content,
                                                comment_indent=comment_indent_level)
    return post_comment_response


@router.post('/vote-comment/{comment_id}')
async def vote_comment(comment_id: int, vote: CommentVote):
    current_user_vote = await check_user_vote_exists_cache_and_db(vote.user_id, comment_id, vote.post_id)
    vote_change_val = determine_vote_change_value(vote, current_user_vote)
    if vote_change_val != 0:
        await insert_or_update_vote_in_db(current_user_vote, vote, comment_id)
        await set_user_vote_in_cache(vote, comment_id)
        await set_or_update_comment_vote_in_cache(vote_change_val, comment_id, vote.post_id)
