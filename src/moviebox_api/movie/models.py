"""
Movies pydantic models
"""
from pydantic import BaseModel
from typing import List

class MovieOrSeriesModel(BaseModel):
    title: str

class EveryoneSearchesModel(BaseModel):
    items: List[MovieOrSeriesModel]