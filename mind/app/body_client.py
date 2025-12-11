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
