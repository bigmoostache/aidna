# AIDNA Project - Environment Branch

This branch focuses on the Environment - the task provider that individuals interact with.
Body and Mind live in individual worktrees (see `individuals/`).

## Architecture

```
┌─────────────────┐
│   ENVIRONMENT   │◄──── Individuals connect here
│   (FastAPI)     │
│   Port 8500     │
└────────┬────────┘
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

- **Individuals** (`individuals/`): Git worktrees for Body + Mind
  - Each individual has its own Body (state) and Mind (logic)
  - LUCA is the base template for all individuals
  - Individuals evolve independently from this environment branch

## Quick Start

```bash
# 1. Start environment (API + PostgreSQL)
./aidna "~,a,d"          # Rebuild + Start

# 2. Generate tasks
curl -X POST http://localhost:8500/tasks/generate \
  -H "Content-Type: application/json" \
  -d '{"seed": 42, "count": 10}'

# 3. Check task stats
curl http://localhost:8500/tasks/stats
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
- **[b] Individuals** - Git worktree management
- **[c] Exploration** - Browse project structure with descriptions
- **[d] Project rules** - Code quality checks
- **[e] Exit** - Exit CLI

### Environment Services (`./aidna a`)
- **Start/Stop/Restart** - Manage docker services
- **Rebuild + Start** - Rebuild images and start
- **FastAPI** - API-specific logs and healthcheck
- **Reset DB** - Stop and remove postgres volume (fresh start)

### Individuals (`./aidna b`)
- **List worktrees** - Show all individuals
- **Create individual** - Branch from LUCA
- **Create LUCA** - Create base individual from main
- **Delete individual** - Remove worktree and branch
- **Show worktree path** - Get path for navigation
- **Prune/Repair** - Maintenance operations

### Ports
| Service | Container | Host Port |
|---------|-----------|-----------|
| Environment API | aidna-api | 8500 |
| PostgreSQL | aidna-postgres | 8532 |

## API Endpoints

### Environment (port 8500)
```
GET  /health                    # Healthcheck
POST /tasks/generate            # Generate tasks {"seed": int, "count": int}
GET  /tasks/next                # Get next pending task
POST /tasks/{id}/submit         # Submit answer {"answer": int}
GET  /tasks/stats               # Task statistics
```

## Project Rules

Run `./aidna "~,d,a"` to check all rules:
- Max 700 lines per file
- Max 7 files per folder
- Max folder depth of 5
- No hardcoded secrets
- All folders have `claude.json` with descriptions
- Cyclomatic complexity under 15
- No linting issues (ruff)
- No security issues (bandit)

## Working with Individuals

Create LUCA (first time):
```bash
./aidna "~,b,c"    # Individuals → Create LUCA
```

Create a new individual:
```bash
./aidna "~,b,b"    # Individuals → Create individual (from LUCA)
```

Navigate to individual:
```bash
cd individuals/luca
./aidna            # Run CLI in that worktree
```
