import random
from datetime import datetime
from uuid import UUID

from db import Task
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def generate_tasks(db: AsyncSession, seed: int, count: int) -> int:
    rng = random.Random(seed)
    tasks = []
    for _ in range(count):
        a = rng.randint(0, 100)
        b = rng.randint(0, 100)
        task = Task(
            seed=seed,
            operand_a=a,
            operand_b=b,
            operator="+",
            correct_answer=a + b,
            reward=1.0,
        )
        tasks.append(task)
    db.add_all(tasks)
    await db.commit()
    return len(tasks)


async def get_next_task(db: AsyncSession) -> Task | None:
    result = await db.execute(
        select(Task)
        .where(Task.status == "pending")
        .order_by(Task.created_at)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def submit_answer(
    db: AsyncSession, task_id: UUID, answer: int
) -> tuple[bool, float, int]:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise ValueError(f"Task {task_id} not found")

    correct = answer == task.correct_answer
    task.submitted_answer = answer
    task.status = "completed" if correct else "failed"
    task.solved_at = datetime.utcnow()
    await db.commit()
    return correct, task.reward if correct else 0.0, task.correct_answer


async def get_stats(db: AsyncSession) -> dict:
    total = await db.execute(select(func.count(Task.id)))
    pending = await db.execute(
        select(func.count(Task.id)).where(Task.status == "pending")
    )
    completed = await db.execute(
        select(func.count(Task.id)).where(Task.status == "completed")
    )
    failed = await db.execute(
        select(func.count(Task.id)).where(Task.status == "failed")
    )
    return {
        "total": total.scalar() or 0,
        "pending": pending.scalar() or 0,
        "completed": completed.scalar() or 0,
        "failed": failed.scalar() or 0,
    }
