import json
from typing import TextIO, Dict, List
import os
import sys
import datetime

myPath = os.path.dirname(os.path.abspath(__file__))
myPath = myPath.split('/tests')[0]
sys.path.insert(0, myPath)

import pytest
from dotenv import load_dotenv

load_dotenv(myPath + '/.env-local-pytests')

from app.models import Comments, CommentEvents
from app.schemas.comments import CommentInfo, CommentUserAndContent, CommentOrder
from .user_fixtures import sample_user, sample_user_2


@pytest.fixture
def sample_comment():
    with open('fixtures/sample_comment.json') as i:
        json_comment = json.load(i)
        return Comments(**json_comment)


@pytest.fixture
def sample_user_comment_content(sample_comment, sample_user):
    return CommentUserAndContent(content=sample_comment.content,
                                 username=sample_user.user_name,
                                 id=sample_comment.id,
                                 parent_comment_id=sample_comment.parent_comment_id)


@pytest.fixture
def sample_comment_2():
    with open('fixtures/sample_comment_2.json') as i:
        json_comment = json.load(i)
        return Comments(**json_comment)


@pytest.fixture
def sample_comment_nested_1():
    with open('fixtures/sample_comment_nested_1.json') as i:
        json_comment = json.load(i)
        return Comments(**json_comment)


@pytest.fixture
def sample_comment_nested_2():
    with open('fixtures/sample_comment_nested_2.json') as i:
        json_comment = json.load(i)
        return Comments(**json_comment)


@pytest.fixture
def sample_comment_nested_3():
    with open('fixtures/sample_comment_nested_3.json') as i:
        json_comment = json.load(i)
        return Comments(**json_comment)


@pytest.fixture
def comments_and_users_multiple(sample_comment, sample_comment_2, sample_user, sample_user_2):
    return [(sample_comment, sample_user), (sample_comment_2, sample_user_2)]


@pytest.fixture
def comments_and_users_multiple_reformatted(comments_and_users_multiple):
    comment_user_and_content = [CommentUserAndContent(username=u.user_name,
                                                      content=c.content,
                                                      parent_comment_id=c.parent_comment_id,
                                                      id=c.id)
                                for c, u in comments_and_users_multiple]
    return comment_user_and_content


@pytest.fixture
def comments_and_users_nested(sample_comment, sample_comment_2, sample_user, sample_user_2,
                              sample_comment_nested_1, sample_comment_nested_2, sample_comment_nested_3):
    return [(sample_comment, sample_user), (sample_comment_2, sample_user_2),
            (sample_comment_nested_1, sample_user_2), (sample_comment_nested_2, sample_user),
            (sample_comment_nested_3, sample_user_2)]


@pytest.fixture
def comment_and_users_nested_reformatted(comments_and_users_nested):
    comment_user_and_content = [CommentUserAndContent(username=u.user_name,
                                                      content=c.content,
                                                      parent_comment_id=c.parent_comment_id,
                                                      id=c.id)
                                for c, u in comments_and_users_nested]
    return comment_user_and_content


def format_json_comment_order(i: TextIO) -> Dict[int, List[int]]:
    json_content_order = json.load(i)
    modified_content_order = {}
    for parent_comment_id in json_content_order:
        modified_content_order[int(parent_comment_id)] = json_content_order[parent_comment_id]
    return modified_content_order


@pytest.fixture
def sample_comment_order() -> List[CommentOrder]:
    comment_order = [CommentOrder(comment_id=1,
                                  created_at=datetime.datetime(2021, 7, 1, 12, 13, 14))]
    return comment_order


@pytest.fixture
def sample_comment_upvote() -> CommentEvents:
    comment_event = CommentEvents(id=1,
                                  created_at=datetime.datetime(2021, 7, 1, 12, 13, 14),
                                  event_name='vote',
                                  user_id=1,
                                  comment_id=1,
                                  event_value='upvote')
    return comment_event


@pytest.fixture
def sample_comment_downvote() -> CommentEvents:
    comment_event = CommentEvents(id=1,
                                  created_at=datetime.datetime(2021, 7, 1, 12, 13, 14),
                                  event_name='vote',
                                  user_id=1,
                                  comment_id=1,
                                  event_value='downvote')
    return comment_event


@pytest.fixture
def sample_comment_order_output():
    with open('fixtures/sample_comment_order_output.json') as i:
        return format_json_comment_order(i)


@pytest.fixture
def sample_comment_order_multiple_output():
    with open('fixtures/sample_comment_order_multiple_output.json') as i:
        return format_json_comment_order(i)


@pytest.fixture
def sample_comment_order_nested_output():
    with open('fixtures/sample_comment_order_nested_output.json') as i:
        return format_json_comment_order(i)


def reformat_json_file_comment_contents(i: TextIO) -> Dict[int, CommentInfo]:
    json_comment_contents = json.load(i)
    modified_comment_contents = {}
    for comment_id in json_comment_contents:
        modified_comment_contents[int(comment_id)] = CommentInfo(**json_comment_contents[comment_id])
    return modified_comment_contents


@pytest.fixture
def sample_comment_contents_output():
    with open('fixtures/sample_comment_contents_output.json') as i:
        return reformat_json_file_comment_contents(i)


@pytest.fixture
def sample_comment_contents_multiple_output():
    with open('fixtures/sample_comment_contents_multiple_output.json') as i:
        return reformat_json_file_comment_contents(i)


@pytest.fixture
def sample_comment_contents_nested_output():
    with open('fixtures/sample_comment_contents_nested_output.json') as i:
        return reformat_json_file_comment_contents(i)


def format_json_comment_indent_layer(i: TextIO) -> Dict[int, int]:
    json_comment_indent_layer = json.load(i)
    modified_comment_indent_layer = {}
    for parent_comment_id in json_comment_indent_layer:
        modified_comment_indent_layer[int(parent_comment_id)] = json_comment_indent_layer[parent_comment_id]
    return modified_comment_indent_layer


@pytest.fixture
def sample_comment_indent_layer_output():
    with open('fixtures/sample_comment_indent_layer_output.json') as i:
        return format_json_comment_indent_layer(i)


@pytest.fixture
def sample_comment_indent_layer_multiple_output():
    with open('fixtures/sample_comment_indent_layer_multiple_output.json') as i:
        return format_json_comment_indent_layer(i)


@pytest.fixture
def sample_comment_indent_layer_nested_output():
    with open('fixtures/sample_comment_indent_layer_nested_output.json') as i:
        return format_json_comment_indent_layer(i)
