from uuid import UUID

from pydantic import BaseModel


class GenerateTasksRequest(BaseModel):
    seed: int
    count: int = 10


class GenerateTasksResponse(BaseModel):
    generated: int
    seed: int


class TaskResponse(BaseModel):
    id: UUID
    operand_a: int
    operand_b: int
    operator: str
    reward: float

    class Config:
        from_attributes = True


class SubmitAnswerRequest(BaseModel):
    answer: int


class SubmitAnswerResponse(BaseModel):
    correct: bool
    reward: float
    correct_answer: int


class TaskStatsResponse(BaseModel):
    total: int
    pending: int
    completed: int
    failed: int
