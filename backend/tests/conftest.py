from fastapi.testclient import TestClient
from app.main import app
import pytest
from mongomock_motor import AsyncMongoMockClient


async def mongodb_client_mock():
    mocked_client = AsyncMongoMockClient()["tests"]
    yield mocked_client


@pytest.fixture(scope="session")
def test_client():
    tclient = TestClient(app)
    yield tclient


# mark this as E2E
# @pytest.fixture(autouse=True)
# async def delete_test_cars(test_client):
#     yield
#     await test_client.app.app.mongodb[Settings.COLLECTION_NAME].delete_many({'brand': '/.*test.*/i'})
