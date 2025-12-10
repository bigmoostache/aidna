# AIDNA Project

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

The CLI auto-starts on first `./aidna` call.

### Navigation

- `a-z` - Select menu option by letter (lowercase)
- `B` - Go back to parent menu (uppercase)
- `R` - Restart CLI, preserves menu state (uppercase)
- `Enter` - Select highlighted option
- `↑/↓` - Navigate menu options (arrow keys)

## CLI Menus

### Main Menu
- **[a] Environment services** - Docker compose management
- **[b] Exploration** - Browse project structure with descriptions
- **[c] Project rules** - Code quality checks
- **[d] Exit** - Exit CLI

### Environment Services
- Start/stop/restart Docker services
- Uses `PORT_PREFIX` from `.env` for port mapping
- Example: `PORT_PREFIX=85` maps postgres to port `8532`

### Exploration
- **Show file structure** - Tree view with descriptions from `claude.json`
- **Set depth** - Control tree depth (default: 3)
- **Select subfolder** - Focus on specific directory

### Project Rules
Automated code quality checks:

| Check | Description |
|-------|-------------|
| **[a] File lengths** | Files exceeding 700 lines |
| **[b] Folder file counts** | Folders with more than 7 files |
| **[c] Spaces in filenames** | Files/folders with spaces in names |
| **[d] Folder depth** | Folders deeper than 5 levels |
| **[e] Hardcoded secrets** | Passwords, API keys, tokens in code |
| **[f] Cyclomatic complexity** | Complex functions (requires `radon`) |
| **[g] Linting issues** | Code style issues (requires `ruff`) |
| **[h] Security issues** | Security vulnerabilities (requires `bandit`) |
| **[i] Check all rules** | Run all checks at once |
| **[j] Update claude.json** | Sync file metadata and descriptions |
| **[k] Missing claude.json** | Folders without documentation |
| **[l] External tool status** | Show installed/missing tools |

#### External Tools (Optional)
```bash
pip install radon ruff bandit
```

## Project Structure

Each folder has a `claude.json` file with metadata:
```json
{
  "filename.py": {
    "type": "file",
    "size_kb": 5.2,
    "lines": 150,
    "description": "Brief description of the file"
  }
}
```

## Project Rules

| Rule | Limit |
|------|-------|
| Max file lines | 700 |
| Max files per folder | 7 |
| Max folder depth | 5 |
| Max cyclomatic complexity | 10 |

## Key Files

```
cli/
  main.py          # CLI entry point and main menu
  core.py          # Shared functions (menus, input, display)
  config.py        # Rule thresholds and patterns
  rules.py         # Rule check implementations
  rules_external.py # External tool integration (radon, ruff, bandit)
  menus/
    services.py    # Environment services menu
    exploration.py # File structure exploration
    rules.py       # Project rules menu
aidna              # CLI control script
environment/
  services/
    docker-compose.yml
.env               # PORT_PREFIX and other config
```

## Modifying the CLI

1. Edit files in `cli/`
2. Run `./aidna R` to restart and reload changes
3. CLI returns to the same menu position after restart
