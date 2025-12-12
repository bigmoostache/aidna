from uuid import UUID

import individual_service
import sacrifice_service
import task_service
from db import Individual, get_db
from fastapi import Depends, FastAPI, HTTPException
from schemas import (
    GenerateTasksRequest,
    GenerateTasksResponse,
    IndividualHeartbeatRequest,
    IndividualRegisterRequest,
    IndividualResponse,
    IndividualsListResponse,
    SacrificeCheckRequest,
    SacrificeCheckResponse,
    SacrificeHistoryResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    TaskResponse,
    TaskStatsResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="AIDNA Environment")


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"healthy": True}


@app.post("/tasks/generate", response_model=GenerateTasksResponse)
async def generate_tasks(
    request: GenerateTasksRequest, db: AsyncSession = Depends(get_db)
):
    count = await task_service.generate_tasks(db, request.seed, request.count)
    return GenerateTasksResponse(generated=count, seed=request.seed)


@app.get("/tasks/next", response_model=TaskResponse | None)
async def get_next_task(db: AsyncSession = Depends(get_db)):
    task = await task_service.get_next_task(db)
    if task is None:
        return None
    return TaskResponse(
        id=task.id,
        operand_a=task.operand_a,
        operand_b=task.operand_b,
        operator=task.operator,
        reward=task.reward,
    )


@app.post("/tasks/{task_id}/submit", response_model=SubmitAnswerResponse)
async def submit_answer(
    task_id: UUID, request: SubmitAnswerRequest, db: AsyncSession = Depends(get_db)
):
    try:
        correct, reward, correct_answer = await task_service.submit_answer(
            db, task_id, request.answer
        )
        return SubmitAnswerResponse(
            correct=correct, reward=reward, correct_answer=correct_answer
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/tasks/stats", response_model=TaskStatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    stats = await task_service.get_stats(db)
    return TaskStatsResponse(**stats)


# === Individual Management ===


def _individual_to_response(individual: Individual) -> IndividualResponse:
    """Convert Individual model to response, formatting datetime fields."""
    return IndividualResponse(
        id=individual.id,
        name=individual.name,
        body_url=individual.body_url,
        registered_at=individual.registered_at.isoformat(),
        last_heartbeat=individual.last_heartbeat.isoformat(),
        energy=individual.energy,
        age=individual.age,
        tasks_solved=individual.tasks_solved,
        alive=individual.alive,
    )


@app.post("/individuals/register", response_model=IndividualResponse)
async def register_individual(
    request: IndividualRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new individual with the environment."""
    individual = await individual_service.register_individual(
        db, request.id, request.name, request.body_url
    )
    return _individual_to_response(individual)


@app.post("/individuals/{individual_id}/heartbeat", response_model=IndividualResponse)
async def individual_heartbeat(
    individual_id: str,
    request: IndividualHeartbeatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update individual's state from heartbeat."""
    individual = await individual_service.heartbeat(
        db,
        individual_id,
        request.energy,
        request.age,
        request.tasks_solved,
        request.alive,
    )
    if individual is None:
        raise HTTPException(status_code=404, detail="Individual not found")
    return _individual_to_response(individual)


@app.get("/individuals", response_model=IndividualsListResponse)
async def list_individuals(db: AsyncSession = Depends(get_db)):
    """Get all registered individuals."""
    individuals = await individual_service.get_all_individuals(db)
    return IndividualsListResponse(
        individuals=[_individual_to_response(i) for i in individuals]
    )


@app.get("/individuals/{individual_id}", response_model=IndividualResponse)
async def get_individual(individual_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific individual by ID."""
    individual = await individual_service.get_individual(db, individual_id)
    if individual is None:
        raise HTTPException(status_code=404, detail="Individual not found")
    return _individual_to_response(individual)


# === Sacrifice/Selection ===


@app.post("/sacrifice/check", response_model=SacrificeCheckResponse)
async def check_sacrifice(
    request: SacrificeCheckRequest = SacrificeCheckRequest(),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually trigger sacrifice check.

    Sacrifices one individual if there are more than min_individuals alive.
    Priority: stale individuals first, then lowest energy.
    """
    victim = await sacrifice_service.check_for_sacrifice(
        db, request.min_individuals
    )
    if victim:
        return SacrificeCheckResponse(
            sacrificed=True,
            victim=_individual_to_response(victim),
        )
    return SacrificeCheckResponse(
        sacrificed=False,
        reason="No eligible victims (not enough individuals or none qualified)",
    )


@app.get("/sacrifice/history", response_model=SacrificeHistoryResponse)
async def sacrifice_history(db: AsyncSession = Depends(get_db)):
    """Get list of all sacrificed (dead) individuals."""
    victims = await sacrifice_service.get_sacrifice_history(db)
    return SacrificeHistoryResponse(
        victims=[_individual_to_response(v) for v in victims]
    )
