import json
import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest

from app.models import Users


@pytest.fixture
def sample_user_2():
    with open('fixtures/sample_user_2.json') as i:
        json_user = json.load(i)
        return Users(**json_user)


@pytest.fixture
def sample_user():
    with open('fixtures/sample_user.json') as i:
        json_user = json.load(i)
        return Users(**json_user)