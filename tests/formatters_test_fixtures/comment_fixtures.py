import json
from typing import TextIO, Dict, List
import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest

from app.models import Comments
from app.schemas.comments import CommentInfo
from .user_fixtures import sample_user, sample_user_2


@pytest.fixture
def sample_comment():
    with open('fixtures/sample_comment.json') as i:
        json_comment = json.load(i)
        return Comments(**json_comment)


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
def comments_and_users_nested(sample_comment, sample_comment_2, sample_user, sample_user_2,
                              sample_comment_nested_1, sample_comment_nested_2, sample_comment_nested_3):
    return [(sample_comment, sample_user), (sample_comment_2, sample_user_2),
            (sample_comment_nested_1, sample_user_2), (sample_comment_nested_2, sample_user),
            (sample_comment_nested_3, sample_user_2)]


def format_json_comment_order(i: TextIO) -> Dict[int, List[int]]:
    json_content_order = json.load(i)
    modified_content_order = {}
    for parent_comment_id in json_content_order:
        modified_content_order[int(parent_comment_id)] = json_content_order[parent_comment_id]
    return modified_content_order


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
