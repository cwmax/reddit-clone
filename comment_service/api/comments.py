from fastapi import APIRouter
from comment_service.schemas.comments import CommentModel, CommentInfo, PostCommentResponse
from comment_service.db.crud.comments import insert_and_cache_comment, get_comment_from_db_with_comment_id
from comment_service.main import db, redis_cache
from comment_service.db.comments import load_and_cache_comment_order, load_and_cache_comment_content
from comment_service.utils.comments import get_comment_indent_level


router = APIRouter()


@router.post('/submit-comment')
async def submit_comment(comment: CommentInfo):
    comment_id = await insert_and_cache_comment(comment)


@router.get('/get-comment/{comment_id}',
            response_model=CommentModel)
async def get_comment(comment_id: int):
    comment = await get_comment_from_db_with_comment_id(comment_id)
    return comment


@router.get('/get-comments/{post_id}',
            response_model=PostCommentResponse)
async def get_post_comments(post_id: int):
    comment_order = await load_and_cache_comment_order(post_id)
    comment_content = await load_and_cache_comment_content(comment_order)
    comment_indent_level = get_comment_indent_level(comment_content)

    post_comment_response = PostCommentResponse(comment_order=comment_order,
                                                comment_content=comment_content,
                                                comment_indent=comment_indent_level)
    return post_comment_response
