import os

import httpx

BODY_URL = os.getenv("BODY_URL", "http://aidna-body:8000")


async def get_memory(key: str) -> str | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BODY_URL}/memory/{key}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()["value"]


async def set_memory(key: str, value: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{BODY_URL}/memory/{key}",
            json={"value": value},
        )
        response.raise_for_status()


async def get_all_memory() -> dict[str, str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BODY_URL}/memory")
        response.raise_for_status()
        return response.json()


async def start_run() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BODY_URL}/runs/start")
        response.raise_for_status()
        return response.json()["run_id"]


async def end_run() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BODY_URL}/runs/end")
        response.raise_for_status()
        return response.json()["run_id"]


# === State/Energy Methods ===


async def get_state() -> dict:
    """Get full body state including energy."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BODY_URL}/state")
        response.raise_for_status()
        return response.json()


async def is_alive() -> bool:
    """Check if body is still alive."""
    state = await get_state()
    return state["alive"]


async def consume_energy(amount: float = 1.0) -> dict:
    """Consume energy and return status."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BODY_URL}/energy/consume",
            json={"amount": amount},
        )
        response.raise_for_status()
        return response.json()


async def gain_energy(amount: float) -> dict:
    """Gain energy from reward."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BODY_URL}/energy/gain",
            json={"amount": amount},
        )
        response.raise_for_status()
        return response.json()
