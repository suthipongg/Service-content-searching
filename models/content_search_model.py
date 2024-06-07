from pydantic import BaseModel
from datetime import datetime
from fastapi import HTTPException

class ContentSearchModel(BaseModel):
    question: str = ''
    top_k: int = 5
    size_search: int = 100
    boost: float = 0.018
    searched_date: datetime = datetime.now()

    def __init__(self, **data):
        super().__init__(**data)
        if not self.question:
            raise HTTPException(status_code=404, detail="question not provided.")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Example Text",
                "top_k": 5,
                "size_search": 100,
                "boost": 0.018
            }
        }
