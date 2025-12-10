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
- `~` - Go to CLI root (main menu)
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
- **CLAUDE.md explorer** - Browse all CLAUDE.md files with parent/children context
- **Set path** - Focus on specific directory
- **Set depth** - Control tree depth (default: 2)

### Project Rules
- **Run all checks** - Execute all code quality checks at once
- **Individual checks** - Run specific checks one at a time
- **Update claude.json** - Sync file metadata across project
- **External tool status** - Show installed/missing optional tools

## Useful Sequences

Common operations starting with `~` to work from anywhere:

```bash
# Run all project checks
./aidna "~,c,a"

# Update all claude.json files
./aidna "~,c,c"

# Show file structure tree
./aidna "~,b,a"

# Browse CLAUDE.md files
./aidna "~,b,b"

# Start docker services
./aidna "~,a,a"

# Stop docker services
./aidna "~,a,b"

# Restart docker services
./aidna "~,a,c"

# Check file lengths
./aidna "~,c,b,a"

# Check folder file counts
./aidna "~,c,b,b"

# Check hardcoded secrets
./aidna "~,c,b,e"

# Check external tool status
./aidna "~,c,d"
```
