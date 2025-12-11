import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = "/app/logs.db"


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                timestamp TEXT NOT NULL,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                request_body TEXT,
                response_body TEXT,
                status_code INTEGER,
                duration_ms REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_run ON request_logs(run_id)")


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def start_run(run_id: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO runs (id, started_at) VALUES (?, ?)",
            (run_id, datetime.utcnow().isoformat())
        )


def end_run(run_id: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE runs SET ended_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), run_id)
        )


def log_request(
    run_id: str | None,
    method: str,
    path: str,
    request_body: str | None,
    response_body: str | None,
    status_code: int,
    duration_ms: float
):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO request_logs
               (run_id, timestamp, method, path, request_body, response_body, status_code, duration_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (run_id, datetime.utcnow().isoformat(), method, path,
             request_body, response_body, status_code, duration_ms)
        )


def get_run_report(run_id: str) -> dict:
    with get_connection() as conn:
        run = conn.execute(
            "SELECT * FROM runs WHERE id = ?", (run_id,)
        ).fetchone()
        if not run:
            return None

        logs = conn.execute(
            """SELECT * FROM request_logs WHERE run_id = ? ORDER BY timestamp""",
            (run_id,)
        ).fetchall()

        memory_ops = {"reads": 0, "writes": 0, "deletes": 0}

        for log in logs:
            path = log["path"]
            method = log["method"]
            if path.startswith("/memory"):
                if method == "GET":
                    memory_ops["reads"] += 1
                elif method == "PUT":
                    memory_ops["writes"] += 1
                elif method == "DELETE":
                    memory_ops["deletes"] += 1

        return {
            "run_id": run_id,
            "started_at": run["started_at"],
            "ended_at": run["ended_at"],
            "total_requests": len(logs),
            "memory_operations": memory_ops,
            "requests": [dict(log) for log in logs]
        }


def get_all_runs() -> list:
    with get_connection() as conn:
        runs = conn.execute(
            "SELECT id, started_at, ended_at FROM runs ORDER BY started_at DESC"
        ).fetchall()
        return [dict(r) for r in runs]


def get_latest_run_id() -> str | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        return row["id"] if row else None
