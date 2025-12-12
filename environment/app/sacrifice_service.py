"""Service for managing sacrifice/selection of individuals."""

import logging
from datetime import datetime, timedelta

from db import Individual
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def check_for_sacrifice(
    db: AsyncSession,
    min_individuals: int = 2,
    stale_threshold_minutes: int = 5,
) -> Individual | None:
    """
    Check if any individual should be sacrificed.

    Rules:
    1. Only sacrifice if > min_individuals alive
    2. Sacrifice stale individuals first (no heartbeat for threshold)
    3. Then sacrifice lowest energy individual

    Returns the sacrificed individual or None if no sacrifice occurred.
    """
    # Get all alive individuals
    result = await db.execute(
        select(Individual)
        .where(Individual.alive.is_(True))
        .order_by(Individual.energy)
    )
    alive = list(result.scalars().all())

    if len(alive) <= min_individuals:
        return None

    stale_threshold = datetime.utcnow() - timedelta(minutes=stale_threshold_minutes)

    # First check for stale individuals
    for individual in alive:
        if individual.last_heartbeat < stale_threshold:
            logger.info(
                f"Sacrificing stale individual: {individual.name} "
                f"(last heartbeat: {individual.last_heartbeat})"
            )
            individual.alive = False
            await db.commit()
            return individual

    # If no stale, sacrifice lowest energy
    victim = alive[0]  # Sorted by energy ascending
    logger.info(
        f"Sacrificing lowest energy individual: {victim.name} "
        f"(energy={victim.energy})"
    )
    victim.alive = False
    await db.commit()
    return victim


async def get_sacrifice_candidates(
    db: AsyncSession,
    min_individuals: int = 2,
) -> list[Individual]:
    """Get individuals that could be sacrificed (lowest energy first)."""
    result = await db.execute(
        select(Individual)
        .where(Individual.alive.is_(True))
        .order_by(Individual.energy)
    )
    alive = list(result.scalars().all())

    if len(alive) <= min_individuals:
        return []

    # Return all except the min_individuals with highest energy
    return alive[: len(alive) - min_individuals]


async def get_sacrifice_history(db: AsyncSession) -> list[Individual]:
    """Get all sacrificed (dead) individuals."""
    result = await db.execute(
        select(Individual).where(Individual.alive.is_(False))
    )
    return list(result.scalars().all())
