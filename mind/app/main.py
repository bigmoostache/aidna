import asyncio
import os
import logging

import env_client
import body_client
import solver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "1.0"))
LOOP_DELAY = float(os.getenv("LOOP_DELAY", "0.1"))


async def wait_for_services():
    logger.info("Waiting for services to be ready...")
    import httpx

    env_url = os.getenv("ENVIRONMENT_URL", "http://aidna-api:8000")
    body_url = os.getenv("BODY_URL", "http://aidna-body:8000")

    for name, url in [("Environment", env_url), ("Body", body_url)]:
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{url}/health", timeout=5.0)
                    if response.status_code == 200:
                        logger.info(f"{name} is ready at {url}")
                        break
            except Exception:
                pass
            logger.info(f"Waiting for {name} at {url}...")
            await asyncio.sleep(2)


async def main_loop():
    tasks_solved = 0
    total_reward = 0.0

    logger.info("Starting main loop...")

    while True:
        try:
            task = await env_client.fetch_next_task()

            if task is None:
                logger.debug("No tasks available, waiting...")
                await asyncio.sleep(POLL_INTERVAL)
                continue

            answer = solver.solve(task)
            result = await env_client.submit_answer(task.id, answer)

            tasks_solved += 1
            if result.correct:
                total_reward += result.reward
                logger.info(
                    f"Task {task.id}: {task.operand_a} {task.operator} {task.operand_b} = {answer} "
                    f"[CORRECT] reward={result.reward} (total: {tasks_solved} solved, {total_reward} reward)"
                )
            else:
                logger.warning(
                    f"Task {task.id}: {task.operand_a} {task.operator} {task.operand_b} = {answer} "
                    f"[WRONG] expected {result.correct_answer}"
                )

            await body_client.set_memory("tasks_solved", str(tasks_solved))
            await body_client.set_memory("total_reward", str(total_reward))
            await body_client.set_memory("last_task_id", str(task.id))

            await asyncio.sleep(LOOP_DELAY)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(POLL_INTERVAL)


async def main():
    logger.info("Mind starting up...")
    await wait_for_services()
    await main_loop()


if __name__ == "__main__":
    asyncio.run(main())
