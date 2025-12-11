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
- **CLAUDE.md explorer** - Browse all CLAUDE.md files with parent/children context
- **Set path** - Focus on specific directory
- **Set depth** - Control tree depth (default: 2)

### Project Rules
- **Run all checks** - Execute all code quality checks at once
- **Individual checks** - Run specific checks one at a time
- **Update claude.json** - Sync file metadata across project
- **External tool status** - Show installed/missing optional tools

## Useful Sequences

All start with `~` to work from anywhere:

- `./aidna " ,~"`: Go back to CLI root
- `./aidna " ,~,c,a"`: Run all project checks
- `./aidna " ,~,c,c"`: Update all claude.json files
- `./aidna " ,~,c,d"`: Check external tool status
- `./aidna " ,~,b,a"`: Show file structure tree
- `./aidna " ,~,b,b"`: Browse CLAUDE.md files
- `./aidna " ,~,a,a"`: Start docker services
- `./aidna " ,~,a,b"`: Stop docker services
- `./aidna " ,~,a,c"`: Restart docker services
