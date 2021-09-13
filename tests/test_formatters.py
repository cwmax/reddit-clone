import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from dotenv import load_dotenv

myPath = myPath.split('/tests')[0]
load_dotenv(myPath + '/.env-local-pytests')

from app.main.formatters import comment_formatters
from formatters_test_fixtures.user_fixtures import sample_user_2, sample_user
from formatters_test_fixtures.comment_fixtures import (sample_comment, sample_comment_2, sample_comment_nested_3,
                                                       sample_comment_nested_1,
                                                       sample_comment_nested_2, comments_and_users_nested,
                                                       comments_and_users_multiple,
                                                       comments_and_users_multiple_reformatted,
                                                       sample_comment_order_multiple_output,
                                                       sample_comment_order_nested_output,
                                                       sample_comment_order_output, sample_comment_contents_output,
                                                       sample_comment_contents_multiple_output,
                                                       sample_comment_contents_nested_output,
                                                       sample_comment_indent_layer_nested_output,
                                                       sample_comment_indent_layer_multiple_output,
                                                       sample_comment_indent_layer_output,
                                                       sample_user_comment_content,
                                                       comment_and_users_nested_reformatted)


def test_format_comment_contents_and_order(sample_user_comment_content, sample_comment_order_output,
                                           sample_comment_contents_output, sample_comment_indent_layer_output):
    comment_order = {}
    comment_contents = {}
    comment_indent_layer = {}

    comment_order, comment_contents, comment_indent_layer = comment_formatters.format_comment_contents_and_order(
        sample_user_comment_content,
        comment_order,
        comment_contents,
        comment_indent_layer,
        post_id=1,
        user_id=None,
        user_authenticated=False)

    assert comment_order == sample_comment_order_output
    assert comment_contents == sample_comment_contents_output
    assert comment_indent_layer == sample_comment_indent_layer_output


def test_format_comments_empty():
    comment_order, comment_contents, comment_indent_layer = comment_formatters.format_comments([], post_id=1,
                                                                                               user_id=1,
                                                                                               user_authenticated=False)
    assert comment_order == {}
    assert comment_contents == {}
    assert comment_indent_layer == {}


def test_format_comments_multiple(comments_and_users_multiple_reformatted, sample_comment_order_multiple_output,
                                  sample_comment_contents_multiple_output,
                                  sample_comment_indent_layer_multiple_output):
    comment_order, comment_contents, comment_indent_layer = comment_formatters.format_comments(
        comments_and_users_multiple_reformatted, post_id=1,
        user_id=1,
        user_authenticated=False)

    assert comment_order == sample_comment_order_multiple_output
    assert comment_contents == sample_comment_contents_multiple_output
    assert comment_indent_layer == sample_comment_indent_layer_multiple_output


def test_format_comments_nested(comment_and_users_nested_reformatted, sample_comment_order_nested_output,
                                sample_comment_contents_nested_output,
                                sample_comment_indent_layer_nested_output):

    comment_order, comment_contents, comment_indent_layer = comment_formatters.format_comments(
        comment_and_users_nested_reformatted,
        post_id=1,
        user_id=None,
        user_authenticated=False)

    assert comment_order == sample_comment_order_nested_output
    assert comment_contents == sample_comment_contents_nested_output
    assert comment_indent_layer == sample_comment_indent_layer_nested_output
