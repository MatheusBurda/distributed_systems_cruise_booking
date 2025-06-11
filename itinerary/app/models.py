from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import List
from datetime import date

@dataclass
class Itinerary(BaseModel):
    id: int
    destination: str
    origin: str
    ship_name: str
    return_port: str
    places_visited: List[str]
    number_of_nights: int
    cabin_cost: float
    cabin_capacity: int
    trip_continent: str
    date: date
    available_cabins: int = Field(ge=0)

    def to_dict(self):
        return self.model_dump()