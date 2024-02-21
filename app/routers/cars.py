from typing import Optional

from fastapi import APIRouter, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.config import Settings
from app.models import CarModelBase, CarModelFull
from app.utils import validate_objectid

cars_router = APIRouter(prefix="/cars", tags=["Cars"])


@cars_router.get("/", summary="List all cars")
async def list_all(
    request: Request,
    page: int = 1,
    page_limit: int = Settings.PAGE_LIMIT,
    min_price: int = 0,
    max_price: int = 10000,
    brand: Optional[str] = None,
):
    if page_limit > Settings.PAGE_LIMIT:
        return HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Page limit needs to be under {Settings.PAGE_LIMIT}",
        )

    skip_docs = (page - 1) * Settings.PAGE_LIMIT

    query = {"price": {"$gt": min_price, "$lt": max_price}}

    if brand:
        query.update({"brand": brand})

    cars = (
        request.app.mongodb[Settings.COLLECTION_NAME]
        .find(query)
        .skip(skip_docs)
        .limit(page_limit)
    )

    results = []
    async for car in cars:
        results.append(CarModelFull(**car))

    return JSONResponse(
        status_code=status.HTTP_200_OK, content=jsonable_encoder(results)
    )


@cars_router.get("/{id}", summary="Get one car details by ID")
async def get_one_car(request: Request, car_id: str):
    car_id = validate_objectid(car_id)
    if not car_id:
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please provide a valid MongoDB ObjectId",
        )

    car = await request.app.mongodb[Settings.COLLECTION_NAME].find_one(
        {"_id": car_id}
    )
    if not car:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(CarModelFull(**car)),
    )


@cars_router.post("/", summary="Add a new car")
async def add_new_car(request: Request, new_car: CarModelBase):
    new_car = new_car.dict()

    doc = await request.app.mongodb[Settings.COLLECTION_NAME].insert_one(
        new_car
    )
    if not doc:
        return HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Request not accepted",
        )

    new_car = await request.app.mongodb[Settings.COLLECTION_NAME].find_one(
        {"_id": doc.inserted_id}
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(CarModelFull(**new_car)),
    )


@cars_router.put("/", summary="Update car information")
async def update_car_information(request: Request, car_data: CarModelFull):
    car_data = car_data.dict(exclude_none=True, exclude_unset=True)

    car_id = validate_objectid(car_data.get("id"))

    update_results = await request.app.mongodb[
        Settings.COLLECTION_NAME
    ].update_one({"_id": car_id}, {"$set": car_data})

    if update_results.matched_count == 0:
        return HTTPException(
            status_code=status.HTTP_200_OK, detail="No matched records"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Success"}
    )


@cars_router.delete("/", summary="Delete one car")
async def delete_one_car(request: Request, car_id: str):
    car_id = validate_objectid(car_id)

    if not car_id:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid ObjectID",
        )

    delete_status = await request.app.mongodb[
        Settings.COLLECTION_NAME
    ].delete_one({"_id": car_id})

    if delete_status.deleted_count == 0:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "success"}
    )
