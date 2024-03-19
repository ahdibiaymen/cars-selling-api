from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.config import Settings
from app.models import CarModelBase, CarModelFull
from app.utils import validate_objectid
from app.database import mongodb_client
from fastapi import Query, Path

cars_router = APIRouter(prefix="/cars", tags=["Cars"])


@cars_router.get("/", summary="List all cars")
async def list_all(
    page: int = Query(default=1, gt=0, description="Page number"),
    page_limit: int = Query(
        default=Settings.PAGE_LIMIT, gt=0, description="Page item limit"
    ),
    min_price: int = Query(default=0, gte=0, description="Minimum price"),
    max_price: int = Query(default=10000, lte=0, description="Maximum price"),
    brand: Optional[str] = Query(
        default=None, lte=0, description="Brand name"
    ),
    db: AsyncIOMotorDatabase = Depends(mongodb_client),
):
    if page_limit > Settings.PAGE_LIMIT:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=f"Page limit needs to be under {Settings.PAGE_LIMIT}",
        )

    skip_docs = (page - 1) * Settings.PAGE_LIMIT

    query = {"price": {"$gt": min_price, "$lt": max_price}}

    if brand:
        query.update({"brand": brand})

    cars = (
        db[Settings.COLLECTION_NAME]
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


@cars_router.get("/{car_id}", summary="Get one car details by ID")
async def get_one_car(
    car_id: str = Path(description="Car ID"),
    db: AsyncIOMotorDatabase = Depends(mongodb_client),
):
    car_id = validate_objectid(car_id)
    if not car_id:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content="Please provide a valid MongoDB ObjectId",
        )

    car = await db[Settings.COLLECTION_NAME].find_one({"_id": car_id})
    if not car:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Car not found"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(CarModelFull(**car)),
    )


@cars_router.post("/", summary="Add a new car")
async def add_new_car(
    new_car: CarModelBase, db: AsyncIOMotorDatabase = Depends(mongodb_client)
):
    new_car = new_car.dict()

    doc = await db[Settings.COLLECTION_NAME].insert_one(new_car)
    if not doc:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content="Request not accepted",
        )

    new_car = await db[Settings.COLLECTION_NAME].find_one(
        {"_id": doc.inserted_id}
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(CarModelFull(**new_car)),
    )


@cars_router.put("/", summary="Update car information")
async def update_car_information(
    car_data: CarModelFull, db: AsyncIOMotorDatabase = Depends(mongodb_client)
):
    car_data = car_data.dict(exclude_none=True, exclude_unset=True)

    car_id = validate_objectid(car_data.get("id"))

    update_results = await db[Settings.COLLECTION_NAME].update_one(
        {"_id": car_id}, {"$set": car_data}
    )

    if update_results.matched_count == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No matched records"},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Success"}
    )


@cars_router.delete("/", summary="Delete one car")
async def delete_one_car(
    car_id: str = Query(description="The car ID to be deleted"),
    db: AsyncIOMotorDatabase = Depends(mongodb_client),
):
    car_id = validate_objectid(car_id)

    if not car_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Please provide a valid ObjectID as car ID",
        )

    delete_status = await db[Settings.COLLECTION_NAME].delete_one(
        {"_id": car_id}
    )

    if delete_status.deleted_count == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Car not found"},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Success"}
    )
