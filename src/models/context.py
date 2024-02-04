from pydantic import BaseModel

class ContextModel(BaseModel):
    started_at: int
    days_posted: list[int]