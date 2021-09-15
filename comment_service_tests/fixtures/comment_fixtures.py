from typing import List, Dict
import datetime

import pytest
from comment_service.schemas.comments import (CommentInfo, CommentModel, CommentOrder, CommentInfoCache,
                                              CommentInfoResponse)


@pytest.fixture(scope='module')
def reuseable_timestamp() -> datetime.datetime:
    timestamp = datetime.datetime.utcnow()
    return timestamp


@pytest.fixture(scope='module')
def reuseable_timestamp_2(reuseable_timestamp) -> datetime.datetime:
    timestamp = reuseable_timestamp + datetime.timedelta(seconds=15)
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


@pytest.fixture
def sample_comment_2(reuseable_timestamp_2):
    sample_comment_2 = CommentInfo(created_at=reuseable_timestamp_2,
                                   author_id=3,
                                   content="test comment 3",
                                   post_id=1,
                                   parent_comment_id=0,
                                   is_deleted=False)
    return sample_comment_2


@pytest.fixture
def sample_comment_3(reuseable_timestamp_2):
    sample_comment_3 = CommentInfo(created_at=reuseable_timestamp_2 + datetime.timedelta(seconds=2),
                                   author_id=11,
                                   content="test comment 4",
                                   post_id=1,
                                   parent_comment_id=1,
                                   is_deleted=False)
    return sample_comment_3


@pytest.fixture
def sample_comment_order(reuseable_timestamp, reuseable_timestamp_2):
    sample_comment_order = [CommentOrder(comment_id=1, created_at=reuseable_timestamp),
                            CommentOrder(comment_id=2, created_at=reuseable_timestamp_2)]
    return sample_comment_order


@pytest.fixture
def sample_comment_contents(sample_comment, sample_comment_2) -> List[CommentInfoCache]:
    sample_comment_contents = {1: CommentInfoCache(**sample_comment.dict()),
                               2: CommentInfoCache(**sample_comment_2.dict())}
    return sample_comment_contents


@pytest.fixture
def sample_comment_content_response(sample_comment, sample_comment_2) -> Dict[str, CommentInfoResponse]:
    sample_comment_content_response = {'1': CommentInfoResponse(username='1', **sample_comment.dict()),
                                       '2': CommentInfoResponse(username='3', **sample_comment_2.dict())}
    return sample_comment_content_response


@pytest.fixture
def sample_comment_indent_levels() -> Dict[str, CommentInfoResponse]:
    sample_comment_indent_levels = {'0': 0, '1': 1, '2': 1}
    return sample_comment_indent_levels


@pytest.fixture
def sample_comment_indent_levels_layered() -> Dict[str, CommentInfoResponse]:
    sample_comment_indent_levels = {'0': 0, '1': 1, '2': 1, '3': 2}
    return sample_comment_indent_levels
