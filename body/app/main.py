from fastapi import FastAPI, HTTPException

from memory import memory
from schemas import MemoryValue

app = FastAPI(title="AIDNA Body")


@app.get("/")
def root():
    return {"status": "ok", "service": "body"}


@app.get("/health")
def health():
    return {"healthy": True}


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
