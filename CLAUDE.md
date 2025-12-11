# AIDNA Project

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   ENVIRONMENT   │     │      BODY       │     │      MIND       │
│   (FastAPI)     │◄────│   (FastAPI)     │◄────│  (Python loop)  │
│   Port 8500     │     │   Port 8501     │     │   (no port)     │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │
    ┌────▼────┐
    │ Postgres│
    │Port 8532│
    └─────────┘
```

### Components

- **Environment** (`environment/`): Task provider with PostgreSQL storage
  - FastAPI app serving task generation and submission endpoints
  - Seedable arithmetic tasks (addition problems)
  - Tracks task status: pending → completed/failed

- **Body** (`body/`): Stateful interface between Mind and Environment
  - Simple key-value memory store
  - REST API for Mind to read/write state
  - Launched before Mind

- **Mind** (`mind/`): Stateless task solver
  - Main loop: fetch task → solve → submit → repeat
  - Hard-coded arithmetic solver
  - Stores progress in Body's memory

## Quick Start

```bash
# 1. Start environment (API + PostgreSQL)
./aidna "~,a,d"          # Rebuild + Start

# 2. Generate tasks
curl -X POST http://localhost:8500/tasks/generate \
  -H "Content-Type: application/json" \
  -d '{"seed": 42, "count": 10}'

# 3. Start Body
./aidna "~,a,f,c"        # Body → Rebuild + Start

# 4. Start Mind (will solve all tasks)
./aidna "~,a,g,c"        # Mind → Rebuild + Start

# 5. Check results
curl http://localhost:8500/tasks/stats
curl http://localhost:8501/memory
```

## CLI Control

Use `./aidna` to interact with the project CLI:

```bash
./aidna              # View current CLI screen
./aidna a            # Press 'a' and view result
./aidna Enter        # Press Enter and view result
./aidna B            # Go back (uppercase)
./aidna R            # Restart CLI (uppercase, reloads code changes)
./aidna "a,b,c"      # Chain multiple keys with commas
./aidna Enter 1.0    # Press key with custom delay (seconds)
```

## CLI Menus

### Main Menu
- **[a] Environment services** - Docker compose management
- **[b] Exploration** - Browse project structure with descriptions
- **[c] Project rules** - Code quality checks
- **[d] Exit** - Exit CLI

### Environment Services (`./aidna a`)
- **Start/Stop/Restart** - Manage docker services
- **Rebuild + Start** - Rebuild images and start
- **FastAPI** - API-specific logs and healthcheck
- **Body** - Body service management
- **Mind** - Mind service management
- **Reset DB** - Stop and remove postgres volume (fresh start)

### Ports
| Service | Container | Host Port |
|---------|-----------|-----------|
| Environment API | aidna-api | 8500 |
| PostgreSQL | aidna-postgres | 8532 |
| Body | aidna-body | 8501 |
| Mind | aidna-mind | (none) |

## API Endpoints

### Environment (port 8500)
```
GET  /health                    # Healthcheck
POST /tasks/generate            # Generate tasks {"seed": int, "count": int}
GET  /tasks/next                # Get next pending task
POST /tasks/{id}/submit         # Submit answer {"answer": int}
GET  /tasks/stats               # Task statistics
```

### Body (port 8501)
```
GET  /health                    # Healthcheck
GET  /memory                    # Get all memory
GET  /memory/{key}              # Get value
PUT  /memory/{key}              # Set value {"value": "string"}
```

## Project Rules

Run `./aidna "~,c,a"` to check all rules:
- Max 700 lines per file
- Max 7 files per folder
- Max folder depth of 5
- No hardcoded secrets
- All folders have `claude.json` with descriptions
- Cyclomatic complexity under 15
- No linting issues (ruff)
- No security issues (bandit)

## Directory Structure

```
aidna/
├── environment/          # Task provider + database
│   ├── app/             # FastAPI application
│   │   ├── main.py      # API endpoints
│   │   ├── db.py        # SQLAlchemy models + connection
│   │   ├── schemas.py   # Pydantic schemas
│   │   └── task_service.py  # Task logic
│   └── services/        # Docker configuration
│       ├── docker-compose.yml
│       └── init.sql     # Database schema
├── body/                # Mind's stateful interface
│   ├── app/
│   │   ├── main.py      # Memory API
│   │   └── memory.py    # Dict-based store
│   └── docker-compose.yml
├── mind/                # Stateless task solver
│   ├── app/
│   │   ├── main.py      # Main loop
│   │   ├── solver.py    # Arithmetic solver
│   │   ├── env_client.py    # Environment API client
│   │   └── body_client.py   # Body API client
│   └── docker-compose.yml
└── cli/                 # Interactive CLI tool
    ├── main.py          # Entry point
    ├── core.py          # Shared utilities
    └── menus/           # Menu implementations
```
