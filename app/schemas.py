from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rubrics: list[str]
    text: str
    created_date: datetime

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    total: int
    results: list[DocumentResponse]

class DeleteResponse(BaseModel):
    message: str
    id: int