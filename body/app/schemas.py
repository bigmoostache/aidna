from pydantic import BaseModel


class MemoryValue(BaseModel):
    value: str


class MemoryEntry(BaseModel):
    key: str
    value: str
