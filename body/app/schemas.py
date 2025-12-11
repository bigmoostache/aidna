from pydantic import BaseModel


class MemoryValue(BaseModel):
    value: str


class MemoryEntry(BaseModel):
    key: str
    value: str


class RunResponse(BaseModel):
    run_id: str
    status: str


class RunInfo(BaseModel):
    id: str
    started_at: str
    ended_at: str | None


class RunListResponse(BaseModel):
    runs: list[RunInfo]


class MemoryOps(BaseModel):
    reads: int
    writes: int
    deletes: int


class RequestLog(BaseModel):
    id: int
    run_id: str | None
    timestamp: str
    method: str
    path: str
    request_body: str | None
    response_body: str | None
    status_code: int
    duration_ms: float


class RunReport(BaseModel):
    run_id: str
    started_at: str
    ended_at: str | None
    total_requests: int
    memory_operations: MemoryOps
    requests: list[RequestLog]
