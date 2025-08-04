from pydantic import BaseModel

class CrimeClusterResponse(BaseModel):
    name: str
    count: int
    level: str
    normalized_count: float

class MetaResponse(BaseModel):
    total_records: int
    filters: dict

class APIResponse(BaseModel):
    meta: MetaResponse
    data: list[CrimeClusterResponse]