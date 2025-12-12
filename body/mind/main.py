import asyncio
import logging
import os

import body_client
import env_client
import solver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "1.0"))
LOOP_DELAY = float(os.getenv("LOOP_DELAY", "0.1"))

# Energy costs (configurable via env)
ENERGY_COST_OBSERVE = float(os.getenv("ENERGY_COST_OBSERVE", "1.0"))
ENERGY_COST_ACT = float(os.getenv("ENERGY_COST_ACT", "1.0"))
ENERGY_REWARD_CORRECT = float(os.getenv("ENERGY_REWARD_CORRECT", "5.0"))
ENERGY_REWARD_WRONG = float(os.getenv("ENERGY_REWARD_WRONG", "0.0"))

# Individual identity (configurable via env)
INDIVIDUAL_NAME = os.getenv("INDIVIDUAL_NAME", "luca")
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "10"))  # Every N tasks


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


async def main_loop(run_id: str):
    tasks_solved = 0
    total_reward = 0.0

    logger.info("Starting main loop...")
    logger.info(
        f"Energy config: observe={ENERGY_COST_OBSERVE}, act={ENERGY_COST_ACT}, "
        f"reward_correct={ENERGY_REWARD_CORRECT}, reward_wrong={ENERGY_REWARD_WRONG}"
    )
    logger.info(f"Heartbeat interval: every {HEARTBEAT_INTERVAL} tasks")

    while True:
        try:
            # Check if still alive
            if not await body_client.is_alive():
                logger.warning("Body is dead! Ending loop.")
                break

            # OBSERVE: Fetch task (costs energy)
            consume_result = await body_client.consume_energy(ENERGY_COST_OBSERVE)
            if not consume_result["alive"]:
                logger.warning("Died during observation! Energy depleted.")
                break

            task = await env_client.fetch_next_task()

            if task is None:
                logger.debug("No tasks available, waiting...")
                await asyncio.sleep(POLL_INTERVAL)
                continue

            # DECIDE: Solve task (free - thinking doesn't cost energy)
            answer = solver.solve(task)

            # ACT: Submit answer (costs energy)
            consume_result = await body_client.consume_energy(ENERGY_COST_ACT)
            if not consume_result["alive"]:
                logger.warning("Died during action! Energy depleted.")
                break

            result = await env_client.submit_answer(task.id, answer)

            # REWARD: Gain energy from correct answers
            tasks_solved += 1
            current_energy = consume_result["energy"]

            if result.correct:
                gain_result = await body_client.gain_energy(ENERGY_REWARD_CORRECT)
                current_energy = gain_result["energy"]
                total_reward += result.reward
                logger.info(
                    f"Task {task.id}: {task.operand_a} {task.operator} {task.operand_b} = {answer} "
                    f"[CORRECT] +{ENERGY_REWARD_CORRECT} energy "
                    f"(energy: {current_energy:.1f}, total: {tasks_solved} solved)"
                )
            else:
                if ENERGY_REWARD_WRONG > 0:
                    gain_result = await body_client.gain_energy(ENERGY_REWARD_WRONG)
                    current_energy = gain_result["energy"]
                logger.warning(
                    f"Task {task.id}: {task.operand_a} {task.operator} {task.operand_b} = {answer} "
                    f"[WRONG] expected {result.correct_answer} "
                    f"(energy: {current_energy:.1f})"
                )

            await body_client.set_memory("tasks_solved", str(tasks_solved))
            await body_client.set_memory("total_reward", str(total_reward))
            await body_client.set_memory("last_task_id", str(task.id))

            # Send heartbeat to Environment every N tasks
            if tasks_solved % HEARTBEAT_INTERVAL == 0:
                try:
                    state = await body_client.get_state()
                    await env_client.send_heartbeat(
                        run_id,
                        state["energy"],
                        state["age"],
                        tasks_solved,
                        state["alive"],
                    )
                    logger.debug(
                        f"Heartbeat sent: energy={state['energy']:.1f}, "
                        f"tasks={tasks_solved}"
                    )
                except Exception as e:
                    logger.warning(f"Heartbeat failed: {e}")

            await asyncio.sleep(LOOP_DELAY)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(POLL_INTERVAL)

    # Log final state and send final heartbeat
    try:
        final_state = await body_client.get_state()
        logger.info(f"Loop ended. Final state: {final_state}")
        logger.info(f"Total tasks solved: {tasks_solved}, Total reward: {total_reward}")
        # Send final heartbeat with alive=False if dead
        await env_client.send_heartbeat(
            run_id,
            final_state["energy"],
            final_state["age"],
            tasks_solved,
            final_state["alive"],
        )
    except Exception:
        pass


async def main():
    logger.info("Mind starting up...")
    await wait_for_services()

    # Start a new run
    run_id = await body_client.start_run()
    logger.info(f"Started run: {run_id}")

    # Register with Environment
    body_url = os.getenv("BODY_URL", "http://aidna-body:8000")
    try:
        await env_client.register_individual(run_id, INDIVIDUAL_NAME, body_url)
        logger.info(f"Registered as '{INDIVIDUAL_NAME}' with Environment")
    except Exception as e:
        logger.warning(f"Failed to register with Environment: {e}")

    try:
        await main_loop(run_id)
    except KeyboardInterrupt:
        logger.info("Interrupted, ending run...")
    finally:
        await body_client.end_run()
        logger.info(f"Ended run: {run_id}")


if __name__ == "__main__":
    asyncio.run(main())
