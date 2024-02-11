from pydantic import BaseModel, field_validator, Field
from typing import Any, Optional
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid Objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoBaseModel(BaseModel):
    id: Field(default_factory=PyObjectId, alias='_id')

    class Config:
        json_encoders = {ObjectId: str}


class CarBase(MongoBaseModel):
    brand: str = Field(..., min_length=3)
    make: int = Field(..., min_length=3)
    year: int = Field(...)
    cm3: int = Field(...)
    km: int = Field(...)
    price: int = Field(...)

    @classmethod
    @field_validator('cm3')
    def ensure_cm3(cls, value: Any):
        if value < 1000 or value > 4000:
            raise ValueError("cm3 value needs to be in range [1000,4000]")
        return value

    @classmethod
    @field_validator('price')
    def ensure_price(cls, value: Any):
        if value < 1000 or value > 10000:
            raise ValueError("cm3 value needs to be in range [1000,10000]")
        return value


class CarUpdate(MongoBaseModel):
    price: Optional[int] = None


class CarDB(CarBase):
    pass
