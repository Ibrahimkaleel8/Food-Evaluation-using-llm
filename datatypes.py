from pydantic import BaseModel
from typing import Optional


class TextIn(BaseModel):
    food_name: str

class Dietinfo(BaseModel):
    name: str
    pros: str
    cons: Optional[str]


