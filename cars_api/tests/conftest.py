import pytest
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app


async def mongodb_client_mock():
    mocked_client = AsyncMongoMockClient()["tests"]
    yield mocked_client


@pytest.fixture(scope="session")
def test_client():
    tclient = TestClient(app)
    yield tclient
