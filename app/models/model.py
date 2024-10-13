from pydantic import BaseModel

class SystemStatsRequest(BaseModel):
    ip: str
