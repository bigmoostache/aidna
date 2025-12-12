"""Service for managing individuals in the environment."""

from datetime import datetime

from db import Individual
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def register_individual(
    db: AsyncSession,
    individual_id: str,
    name: str,
    body_url: str,
) -> Individual:
    """Register a new individual or update existing."""
    result = await db.execute(
        select(Individual).where(Individual.id == individual_id)
    )
    individual = result.scalar_one_or_none()

    if individual:
        # Update existing individual
        individual.last_heartbeat = datetime.utcnow()
        individual.alive = True
        individual.body_url = body_url
    else:
        # Create new individual
        individual = Individual(
            id=individual_id,
            name=name,
            body_url=body_url,
        )
        db.add(individual)

    await db.commit()
    await db.refresh(individual)
    return individual


async def heartbeat(
    db: AsyncSession,
    individual_id: str,
    energy: float,
    age: int,
    tasks_solved: int,
    alive: bool,
) -> Individual | None:
    """Update individual's state from heartbeat."""
    result = await db.execute(
        select(Individual).where(Individual.id == individual_id)
    )
    individual = result.scalar_one_or_none()

    if individual:
        individual.last_heartbeat = datetime.utcnow()
        individual.energy = energy
        individual.age = age
        individual.tasks_solved = tasks_solved
        individual.alive = alive
        await db.commit()
        await db.refresh(individual)

    return individual


async def get_all_individuals(db: AsyncSession) -> list[Individual]:
    """Get all registered individuals."""
    result = await db.execute(select(Individual).order_by(Individual.name))
    return list(result.scalars().all())


async def get_alive_individuals(db: AsyncSession) -> list[Individual]:
    """Get all alive individuals, sorted by energy (ascending for sacrifice)."""
    result = await db.execute(
        select(Individual)
        .where(Individual.alive.is_(True))
        .order_by(Individual.energy)
    )
    return list(result.scalars().all())


async def get_individual(db: AsyncSession, individual_id: str) -> Individual | None:
    """Get a specific individual by ID."""
    result = await db.execute(
        select(Individual).where(Individual.id == individual_id)
    )
    return result.scalar_one_or_none()
