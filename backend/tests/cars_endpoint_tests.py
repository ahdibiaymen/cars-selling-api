import pytest
from app.database import mongodb_client
from app.models import CarModelBase
from conftest import mongodb_client_mock
from unittest import mock
import json
from dotmap import DotMap

TEST_DATA = [
    {
        "_id": "65d804debfef2fc45309aeb8",
        "brand": "Fiat",
        "make": "Doblo",
        "year": 2015,
        "price": 7300,
        "km": 115000,
        "gearbox": "M",
        "doors": "4/5",
        "imported": "0",
        "kW": "55",
        "cm3": 1248.0,
        "fuel": "diesel",
        "registered": "1",
        "color": "WH",
        "aircon": "2",
        "damage": "0",
        "car_type": "PU",
        "standard": "5",
        "drive": "F",
    },
    {
        "_id": "65d8060ca6f1b4a3fab582a9",
        "brand": "Fiat",
        "make": "Doblo",
        "year": 2015,
        "price": 5990,
        "km": 71000,
        "gearbox": "M",
        "doors": "2/3",
        "imported": "0",
        "kW": "66",
        "cm3": 1248.0,
        "fuel": "diesel",
        "registered": "1",
        "color": "WH",
        "aircon": "2",
        "damage": "0",
        "car_type": "PU",
        "standard": "5",
        "drive": "F",
    },
    {
        "_id": "65d8061ea6f1b4a3fab582aa",
        "brand": "Citroen",
        "make": "C3",
        "year": 2004,
        "price": 2050,
        "km": 203415,
        "gearbox": "M",
        "doors": "4/5",
        "imported": "0",
        "kW": "50",
        "cm3": 1398.0,
        "fuel": "diesel",
        "registered": "0",
        "color": "BL",
        "aircon": "4",
        "damage": "0",
        "car_type": "SDN",
        "standard": "3",
        "drive": "F",
    },
]


@pytest.mark.asyncio
def test_list_all_cars_success(test_client):

    class AsyncMockIterator:
        def __init__(self, items):
            self.items = items

        def __aiter__(self):
            return self

        async def __anext__(self):
            if not self.items:
                raise StopAsyncIteration
            return self.items.pop(0)

    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    # Create a mock cursor
    mock_cursor = mock.MagicMock()
    mock_cursor.limit = mock.MagicMock(
        return_value=AsyncMockIterator(TEST_DATA)
    )

    with mock.patch("app.tests.conftest.AsyncMongoMockClient") as mock_client:
        mock_client.return_value.__getitem__.return_value.__getitem__.return_value.find.return_value.skip.return_value = (
            mock_cursor
        )

        response = test_client.get("/cars")
        assert response.status_code == 200
        assert response.json()[0]["_id"] == "65d804debfef2fc45309aeb8"
        assert response.json()[1]["_id"] == "65d8060ca6f1b4a3fab582a9"
        assert response.json()[2]["_id"] == "65d8061ea6f1b4a3fab582aa"


@pytest.mark.asyncio
def test_list_all_exceeding_page_limit(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    params = {"page_limit": 26}
    response = test_client.get("/cars", params=params)
    assert response.status_code == 406


@pytest.mark.asyncio
def test_list_all_invalid_page_number(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    # negative
    params = {"page": -1}
    response = test_client.get("/cars", params=params)
    assert response.status_code == 422

    # zero
    params = {"page": 0}
    response = test_client.get("/cars", params=params)
    assert response.status_code == 422


@pytest.mark.asyncio
def test_list_all_invalid_page_limit(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    # negative
    params = {"page_limit": -1}
    response = test_client.get("/cars", params=params)
    assert response.status_code == 422

    # zero
    params = {"page_limit": 0}
    response = test_client.get("/cars", params=params)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_one_car_success(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    mocked_collection = mock.AsyncMock()
    mocked_collection.find_one = mock.AsyncMock(return_value=TEST_DATA[0])

    with mock.patch("app.tests.conftest.AsyncMongoMockClient") as mock_client:
        mock_client.return_value.__getitem__.return_value.__getitem__.return_value = (
            mocked_collection
        )

        response = test_client.get("/cars/65d804debfef2fc45309aeb8")
        assert response.status_code == 200
        assert response.json()["_id"] == "65d804debfef2fc45309aeb8"


@pytest.mark.asyncio
async def test_list_one_car_bad_ID(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock
    response = test_client.get("/cars/something_like_id")
    assert response.status_code == 422
    response = test_client.get("/cars/cbcde")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_one_car_none_existing_ID(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock
    response = test_client.get("/cars/65d804debfef2bcf5309aeb8")
    assert response.status_code == 404
    assert response.json() == "Car not found"


@pytest.mark.asyncio
async def test_add_new_car_success(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock
    mocked_collection = mock.AsyncMock()
    insert_one_results = DotMap({"inserted_id": TEST_DATA[0].get("_id")})
    mocked_collection.insert_one = mock.AsyncMock(
        return_value=insert_one_results
    )
    mocked_collection.find_one = mock.AsyncMock(return_value=TEST_DATA[0])

    with mock.patch("app.tests.conftest.AsyncMongoMockClient") as mock_client:
        mock_client.return_value.__getitem__.return_value.__getitem__.return_value = (
            mocked_collection
        )
        post_data = json.dumps(
            CarModelBase(
                **{k: v for k, v in TEST_DATA[0].items() if k not in {"_id"}}
            ).dict()
        )
        response = test_client.post("/cars/", data=post_data)
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_add_new_car_missing_fields(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock
    # missing brand
    post_data = {
        "make": "Doblo",
        "year": 2015,
        "cm3": 1248,
        "km": 115000,
        "price": 7300,
    }
    response = test_client.post("/cars/", data=json.dumps(post_data))
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "missing"
    assert response.json()["detail"][0]["msg"] == "Field required"


@pytest.mark.asyncio
async def test_add_new_car_missing_bad_field_structure(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock
    # brand name that does not respect the minimum length requirement
    # price that does not respect the minimum value required
    post_data = {
        "brand": "A",
        "make": "Doblo",
        "year": 2015,
        "cm3": 1248,
        "km": 115000,
        "price": 800,
    }
    response = test_client.post("/cars/", data=json.dumps(post_data))
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "string_too_short"
    assert (
        response.json()["detail"][0]["msg"]
        == "String should have at least 2 characters"
    )
    assert response.json()["detail"][0]["loc"][1] == "brand"
    assert response.json()["detail"][1]["type"] == "greater_than_equal"
    assert (
        response.json()["detail"][1]["msg"]
        == "Input should be greater than or equal to 1000"
    )
    assert response.json()["detail"][1]["loc"][1] == "price"


@pytest.mark.asyncio
async def test_update_car_no_matched_records(test_client):

    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    mocked_collection = mock.AsyncMock()
    mocked_collection.update_one.return_value = DotMap({"matched_count": 0})

    post_data = {
        "_id": "65d804debfef2fc45309aeb8",
        "brand": "Fiat",
        "make": "Doblo",
        "year": 2015,
        "cm3": 1248,
        "km": 115000,
        "price": 4800,
    }
    with mock.patch(
        "app.tests.conftest.AsyncMongoMockClient"
    ) as mocked_client:
        mocked_client.return_value.__getitem__.return_value.__getitem__.return_value = (
            mocked_collection
        )
        response = test_client.put("/cars/", data=json.dumps(post_data))
        assert response.status_code == 404
        assert response.json() == {"message": "No matched records"}


@pytest.mark.asyncio
async def test_update_car_success(test_client):

    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    mocked_collection = mock.AsyncMock()
    mocked_collection.update_one.return_value = DotMap({"matched_count": 1})

    post_data = {
        "_id": "65d804debfef2fc45309aeb8",
        "brand": "Fiat",
        "make": "Doblo",
        "year": 2015,
        "cm3": 1248,
        "km": 115000,
        "price": 4800,
    }
    with mock.patch(
        "app.tests.conftest.AsyncMongoMockClient"
    ) as mocked_client:
        mocked_client.return_value.__getitem__.return_value.__getitem__.return_value = (
            mocked_collection
        )
        response = test_client.put("/cars/", data=json.dumps(post_data))
        assert response.status_code == 200
        assert response.json() == {"message": "Success"}


@pytest.mark.asyncio
async def test_update_car_invalid_id(test_client):

    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    post_data = {
        "_id": "123",
        "brand": "Fiat",
        "make": "Doblo",
        "year": 2015,
        "cm3": 1248,
        "km": 115000,
        "price": 4800,
    }
    response = test_client.put("/cars/", data=json.dumps(post_data))
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "Input should be an instance of ObjectId"
    )


@pytest.mark.asyncio
async def test_update_car_invalid_fields(test_client):

    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    # invalid price and invalid brand name (requirements not respected)
    post_data = {
        "_id": "65d804debfef2fc45309aeb8",
        "brand": "A",
        "make": "Doblo",
        "year": 2015,
        "cm3": 1248,
        "km": 115000,
        "price": 1,
    }
    response = test_client.put("/cars/", data=json.dumps(post_data))
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "string_too_short"
    assert (
        response.json()["detail"][0]["msg"]
        == "String should have at least 2 characters"
    )
    assert response.json()["detail"][0]["loc"][1] == "brand"
    assert response.json()["detail"][1]["type"] == "greater_than_equal"
    assert (
        response.json()["detail"][1]["msg"]
        == "Input should be greater than or equal to 1000"
    )
    assert response.json()["detail"][1]["loc"][1] == "price"


@pytest.mark.asyncio
async def test_delete_one_car_success(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    mocked_collection = mock.AsyncMock()
    mocked_collection.delete_one.return_value = DotMap({"deleted_count": 1})

    with mock.patch(
        "app.tests.conftest.AsyncMongoMockClient"
    ) as mocked_client:
        mocked_client.return_value.__getitem__.return_value.__getitem__.return_value = (
            mocked_collection
        )
        data = {"car_id": TEST_DATA[0]["_id"]}
        response = test_client.delete("/cars/", params=data)
        assert response.status_code == 200
        assert response.json() == {"message": "Success"}


@pytest.mark.asyncio
async def test_delete_one_car_not_found(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    mocked_collection = mock.AsyncMock()
    mocked_collection.delete_one.return_value = DotMap({"deleted_count": 0})

    with mock.patch(
        "app.tests.conftest.AsyncMongoMockClient"
    ) as mocked_client:
        mocked_client.return_value.__getitem__.return_value.__getitem__.return_value = (
            mocked_collection
        )
        data = {"car_id": TEST_DATA[0]["_id"]}
        response = test_client.delete("/cars/", params=data)
        assert response.status_code == 404
        assert response.json() == {"message": "Car not found"}


@pytest.mark.asyncio
async def test_delete_one_car_bad_id(test_client):
    test_client.app.dependency_overrides[mongodb_client] = mongodb_client_mock

    data = {"car_id": 1234}
    response = test_client.delete("/cars/", params=data)
    assert response.status_code == 400
    assert response.json() == "Please provide a valid ObjectID as car ID"

    data = {"car_id": "test"}
    response = test_client.delete("/cars/", params=data)
    assert response.status_code == 400
    assert response.json() == "Please provide a valid ObjectID as car ID"
