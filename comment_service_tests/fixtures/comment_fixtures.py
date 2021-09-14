import datetime

import pytest
from comment_service.schemas.comments import CommentInfo, CommentModel


@pytest.fixture(scope='module')
def reuseable_timestamp() -> datetime.datetime:
    timestamp = datetime.datetime.utcnow()
    return timestamp


@pytest.fixture
def sample_comment_response(reuseable_timestamp) -> CommentModel:
    sample_comment = CommentModel(created_at=reuseable_timestamp,
                                  author_id=1,
                                  content="test second comment",
                                  post_id=1,
                                  parent_comment_id=0,
                                  is_deleted=False,
                                  id=1)
    return sample_comment


@pytest.fixture
def sample_comment(reuseable_timestamp) -> CommentInfo:
    sample_comment = CommentInfo(created_at=reuseable_timestamp,
                                  author_id=1,
                                  content="test second comment",
                                  post_id=1,
                                  parent_comment_id=0,
                                  is_deleted=False)
    return sample_comment
