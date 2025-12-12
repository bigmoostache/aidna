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


# === Individual Schemas ===


class IndividualRegisterRequest(BaseModel):
    id: str
    name: str
    body_url: str


class IndividualHeartbeatRequest(BaseModel):
    energy: float
    age: int
    tasks_solved: int
    alive: bool


class IndividualResponse(BaseModel):
    id: str
    name: str
    body_url: str
    registered_at: str
    last_heartbeat: str
    energy: float
    age: int
    tasks_solved: int
    alive: bool

    class Config:
        from_attributes = True


class IndividualsListResponse(BaseModel):
    individuals: list[IndividualResponse]


# === Sacrifice Schemas ===


class SacrificeCheckRequest(BaseModel):
    min_individuals: int = 2


class SacrificeCheckResponse(BaseModel):
    sacrificed: bool
    victim: IndividualResponse | None = None
    reason: str | None = None


class SacrificeHistoryResponse(BaseModel):
    victims: list[IndividualResponse]
