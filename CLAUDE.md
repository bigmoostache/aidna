# AIDNA Individual - LUCA

LUCA (Last Universal Common Ancestor) is the base template for all individuals.
Individuals diverge from LUCA and evolve independently from the main environment branch.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│      BODY       │     │      MIND       │
│   (FastAPI)     │◄────│  (Python loop)  │
│   Port 8501     │     │   (no port)     │
└─────────────────┘     └─────────────────┘
```

### Components

- **Body** (`body/`): Stateful interface for Mind
  - Simple key-value memory store
  - REST API for Mind to read/write state
  - Launched before Mind

- **Mind** (`mind/`): Stateless agent
  - Main loop: perceive → decide → act → repeat
  - Stores progress in Body's memory

## Quick Start

```bash
# 1. Start Body
./aidna "~,a,a,c"        # Services → Body → Rebuild + Start

# 2. Start Mind
./aidna "~,a,b,c"        # Services → Mind → Rebuild + Start

# 3. Check memory state
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
- **[a] Services** - Docker compose management (Body, Mind)
- **[b] Individuals** - Git worktree management
- **[c] Exploration** - Browse project structure with descriptions
- **[d] Project rules** - Code quality checks
- **[e] Exit** - Exit CLI

### Services (`./aidna a`)
- **Body** - Body service management
- **Mind** - Mind service management

### Ports
| Service | Container | Host Port |
|---------|-----------|-----------|
| Body | aidna-body | 8501 |
| Mind | aidna-mind | (none) |

## API Endpoints

### Body (port 8501)
```
GET  /health                    # Healthcheck
GET  /memory                    # Get all memory
GET  /memory/{key}              # Get value
PUT  /memory/{key}              # Set value {"value": "string"}
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

## Creating New Individuals

From the main repository, use the CLI:
```bash
./aidna "~,b,b"    # Individuals → Create individual (from LUCA)
```

Or manually:
```bash
git worktree add individuals/<name> -b <name> luca
```
