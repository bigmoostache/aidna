from uuid import UUID

import task_service
from db import get_db
from fastapi import Depends, FastAPI, HTTPException
from schemas import (
    GenerateTasksRequest,
    GenerateTasksResponse,
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
