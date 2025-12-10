# CLI Development Guide

## Architecture

The CLI uses a menu stack pattern for navigation. Each menu pushes its state onto the stack when entering submenus and pops when returning.

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point, main menu, state restoration |
| `core.py` | Shared functions (menus, input, display, key handling) |
| `config.py` | Rule thresholds and patterns |
| `rules.py` | Built-in rule check implementations |
| `rules_external.py` | External tool integration (radon, ruff, bandit) |
| `menus/` | Individual menu implementations |

## Project Rules

| Rule | Limit | Config Key |
|------|-------|------------|
| Max file lines | 700 | `MAX_FILE_LINES` |
| Max files per folder | 7 | `MAX_FOLDER_FILES` |
| Max folder depth | 5 | `MAX_FOLDER_DEPTH` |
| Max cyclomatic complexity | 10 | `MAX_CYCLOMATIC_COMPLEXITY` |

## Adding a New Menu

1. Create `menus/your_menu.py` with a function `your_menu(menu_stack, initial_selected=0)`
2. Export it in `menus/__init__.py`
3. Import and add handler in `main.py:run_from_state()` for restart support
4. Call from parent menu with:
```python
menu_stack.append({'menu': 'your_menu', 'selected': 0})
your_menu(menu_stack)
menu_stack.pop()
```

## Adding a New Rule Check

1. Add threshold constants to `config.py`
2. Implement check function in `rules.py` returning list of violations
3. Add display wrapper in `menus/rules.py`
4. Add to `_check_all_rules()` summary

## External Tools (Optional)

```bash
pip install radon ruff bandit
```

- **radon** - Cyclomatic complexity analysis
- **ruff** - Fast Python linter
- **bandit** - Security vulnerability scanner

## Navigation System

| Key | Action | Handler |
|-----|--------|---------|
| `a-z` | Select menu option | `select_menu()` |
| `~` | Go to CLI root | `GoToRoot` exception |
| `B` | Go back one level | Returns `-1` |
| `R` | Restart CLI | `RestartRequested` exception |
| `↑/↓` | Navigate options | Arrow key sequences |
| `Enter` | Confirm selection | Returns selected index |

## State Persistence

On restart (`R`), menu state is saved to `.state.json` and restored after Python restarts. The shell wrapper (`cli.sh`) keeps tmux alive.

## Modifying the CLI

1. Edit files in `cli/`
2. Run `./aidna R` to restart and reload changes
3. CLI returns to the same menu position after restart
