import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from dotenv import load_dotenv
myPath = myPath.split('/comment_service_tests')[0]
load_dotenv(myPath+'/.env-local-pytests')

import pytest
from fastapi.testclient import TestClient

from comment_service.main import get_application


@pytest.fixture
def client() -> TestClient:
    app = get_application()
    test_client = TestClient(app)
    yield test_client
