from pydantic import BaseModel, field_validator
from typing import List, Union, Optional


class TextIn(BaseModel):
    food_name: str


class NameResponse(BaseModel):
    name: str
    type: Optional[str] = None
    ingredients: Optional[str] = None


class Vitamins(BaseModel):
    items: List[str]

    @field_validator("items")
    def split_items(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",")]
        return value


class Minerals(BaseModel):
    items: List[str]

    @field_validator("items")
    def split_items(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",")]
        return value


class Nutrients(BaseModel):
    name: str
    proteins: str
    fats: str
    carbohydrates: str
    vitamins: Union[Vitamins, str]
    minerals: Union[Minerals, str]


class Sentence(BaseModel):
    response: str


class FinalResponse(BaseModel):
    body: Nutrients
    sentence: Sentence
