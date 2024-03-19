from typing import Optional

from pydantic import BaseModel, Field
from pydantic_mongo import ObjectIdField


class CarModelBase(BaseModel):
    brand: str = Field(..., min_length=2)
    make: str = Field(..., min_length=2)
    year: int = Field(...)
    cm3: int = Field(..., ge=1000, le=4000)
    km: int = Field(...)
    price: int = Field(..., ge=1000, le=100000)

    def __init__(self, /, **data):
        data["make"] = str(
            data.get("make", "")
        )  # Convert 'make' to a string for models with make as int
        super().__init__(**data)


class CarModelFull(CarModelBase):
    id: Optional[ObjectIdField] = Field(alias="_id")
