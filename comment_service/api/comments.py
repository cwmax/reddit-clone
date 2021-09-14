from fastapi import APIRouter
from comment_service.schemas.comments import CommentModel, CommentInfo
from comment_service.db.crud.comments import insert_comment_into_db, get_comment_from_db_with_comment_id
from comment_service.main import db


router = APIRouter()


@router.post('/submit-comment')
async def submit_comment(comment: CommentInfo):
    await insert_comment_into_db(comment)


@router.get('/get-comment/{comment_id}',
            response_model=CommentModel)
async def submit_comment(comment_id: int):
    comment = await get_comment_from_db_with_comment_id(comment_id)
    return comment
