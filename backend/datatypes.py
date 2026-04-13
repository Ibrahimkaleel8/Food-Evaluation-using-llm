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


# --- V2 Models ---
from enum import Enum

class HealthCondition(str, Enum):
    NONE = "none"
    DIABETES = "diabetes"
    HYPERTENSION = "hypertension"
    HIGH_CHOLESTEROL = "high_cholesterol"
    OBESITY = "obesity"

class UserProfile(BaseModel):
    age: int
    weight_kg: float
    goal: str
    conditions: list[HealthCondition] = []

class NutritionResponse(BaseModel):
    food_name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    key_vitamins: list[str]
    health_score: float
    recommendation: str
    confidence: float
    retrieval_source: str
