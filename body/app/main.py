import time
import uuid

import logging_db
from fastapi import FastAPI, HTTPException, Request, Response
from memory import memory
from schemas import (
    ConsumeRequest,
    ConsumeResponse,
    EnergyResponse,
    GainRequest,
    GainResponse,
    MemoryValue,
    RunListResponse,
    RunReport,
    RunResponse,
    StateResponse,
)
from starlette.middleware.base import BaseHTTPMiddleware
from state import state

app = FastAPI(title="AIDNA Body")

# Current active run ID (set via /runs/start)
current_run_id: str | None = None


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Read request body
        body = await request.body()
        request_body = body.decode() if body else None

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Read response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        # Log to database (skip health/root checks to reduce noise)
        path = request.url.path
        if path not in ["/", "/health"] and not path.startswith("/runs"):
            logging_db.log_request(
                run_id=current_run_id,
                method=request.method,
                path=path,
                request_body=request_body,
                response_body=response_body.decode() if response_body else None,
                status_code=response.status_code,
                duration_ms=duration_ms
            )

        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )


app.add_middleware(LoggingMiddleware)


@app.on_event("startup")
def startup():
    logging_db.init_db()


@app.get("/")
def root():
    return {"status": "ok", "service": "body"}


@app.get("/health")
def health():
    return {"healthy": True}


# === Run Management ===

@app.post("/runs/start", response_model=RunResponse)
def start_run():
    global current_run_id
    current_run_id = str(uuid.uuid4())
    logging_db.start_run(current_run_id)
    memory.clear()  # Clear memory for fresh run
    state.reset()  # Reset state (energy, age) for fresh run
    return RunResponse(run_id=current_run_id, status="started")


@app.post("/runs/end", response_model=RunResponse)
def end_run():
    global current_run_id
    if current_run_id is None:
        raise HTTPException(status_code=400, detail="No active run")
    logging_db.end_run(current_run_id)
    ended_id = current_run_id
    current_run_id = None
    return RunResponse(run_id=ended_id, status="ended")


@app.get("/runs", response_model=RunListResponse)
def list_runs():
    runs = logging_db.get_all_runs()
    return RunListResponse(runs=runs)


@app.get("/runs/current")
def get_current_run():
    return {"run_id": current_run_id}


@app.get("/runs/latest/report", response_model=RunReport)
def get_latest_report():
    run_id = logging_db.get_latest_run_id()
    if run_id is None:
        raise HTTPException(status_code=404, detail="No runs found")
    report = logging_db.get_run_report(run_id)
    return RunReport(**report)


@app.get("/runs/{run_id}/report", response_model=RunReport)
def get_run_report(run_id: str):
    report = logging_db.get_run_report(run_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return RunReport(**report)


# === Memory Operations ===

@app.get("/memory")
def get_all_memory():
    return memory.get_all()


@app.get("/memory/{key}")
def get_memory(key: str):
    value = memory.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    return {"key": key, "value": value}


@app.put("/memory/{key}")
def set_memory(key: str, data: MemoryValue):
    memory.set(key, data.value)
    return {"key": key, "value": data.value}


@app.delete("/memory/{key}")
def delete_memory(key: str):
    if memory.delete(key):
        return {"deleted": True, "key": key}
    raise HTTPException(status_code=404, detail=f"Key '{key}' not found")


@app.delete("/memory")
def clear_memory():
    memory.clear()
    return {"cleared": True}


# === State/Energy Operations ===


@app.get("/state", response_model=StateResponse)
def get_state():
    """Get full body state including energy."""
    return StateResponse(**state.to_dict())


@app.get("/energy", response_model=EnergyResponse)
def get_energy():
    """Get current energy level."""
    return EnergyResponse(energy=state.energy, alive=state.alive)


@app.post("/energy/consume", response_model=ConsumeResponse)
def consume_energy(request: ConsumeRequest):
    """Consume energy. Returns alive status."""
    alive = state.consume_energy(request.amount)
    return ConsumeResponse(consumed=request.amount, energy=state.energy, alive=alive)


@app.post("/energy/gain", response_model=GainResponse)
def gain_energy(request: GainRequest):
    """Gain energy from rewards."""
    state.gain_energy(request.amount)
    return GainResponse(gained=request.amount, energy=state.energy)
