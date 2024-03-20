from app.database import mongodb_client


# mark this test as E2E test with pytest
def test_mongodb_client():
    client = mongodb_client()
    assert client is not None
