import os
from uuid import UUID

import httpx
from pydantic import BaseModel

ENVIRONMENT_URL = os.getenv("ENVIRONMENT_URL", "http://aidna-api:8000")


class Task(BaseModel):
    id: UUID
    operand_a: int
    operand_b: int
    operator: str
    reward: float


class SubmitResult(BaseModel):
    correct: bool
    reward: float
    correct_answer: int


async def fetch_next_task() -> Task | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ENVIRONMENT_URL}/tasks/next")
        response.raise_for_status()
        data = response.json()
        if data is None:
            return None
        return Task(**data)


async def submit_answer(task_id: UUID, answer: int) -> SubmitResult:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ENVIRONMENT_URL}/tasks/{task_id}/submit",
            json={"answer": answer},
        )
        response.raise_for_status()
        return SubmitResult(**response.json())


# === Individual Registration/Heartbeat ===


async def register_individual(individual_id: str, name: str, body_url: str) -> dict:
    """Register this individual with the environment."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ENVIRONMENT_URL}/individuals/register",
            json={"id": individual_id, "name": name, "body_url": body_url},
        )
        response.raise_for_status()
        return response.json()


async def send_heartbeat(
    individual_id: str,
    energy: float,
    age: int,
    tasks_solved: int,
    alive: bool,
) -> dict:
    """Send heartbeat with current state."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ENVIRONMENT_URL}/individuals/{individual_id}/heartbeat",
            json={
                "energy": energy,
                "age": age,
                "tasks_solved": tasks_solved,
                "alive": alive,
            },
        )
        response.raise_for_status()
        return response.json()
