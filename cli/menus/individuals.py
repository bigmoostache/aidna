import os
import subprocess

from cli.core import PROJECT_ROOT, input_str, run_command, select_menu, show_output

INDIVIDUALS_DIR = os.path.join(PROJECT_ROOT, "individuals")


def get_worktrees():
    """Get list of worktrees as (path, branch, commit) tuples."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        return []

    worktrees = []
    current = {}
    for line in result.stdout.strip().split('\n'):
        if line.startswith('worktree '):
            current = {'path': line[9:]}
        elif line.startswith('HEAD '):
            current['commit'] = line[5:8]
        elif line.startswith('branch '):
            current['branch'] = line[7:].replace('refs/heads/', '')
        elif line == '' and current:
            worktrees.append(current)
            current = {}
    if current:
        worktrees.append(current)

    return worktrees


def get_individuals():
    """Get worktrees that are in the individuals folder."""
    worktrees = get_worktrees()
    return [w for w in worktrees if w.get('path', '').startswith(INDIVIDUALS_DIR)]


def list_worktrees_action():
    """Show all worktrees."""
    worktrees = get_worktrees()
    if not worktrees:
        show_output("Worktrees", ["No worktrees found."])
        return

    lines = []
    for w in worktrees:
        path = w.get('path', 'unknown')
        branch = w.get('branch', 'detached')
        commit = w.get('commit', '???')
        is_individual = path.startswith(INDIVIDUALS_DIR)
        marker = " [individual]" if is_individual else " [main]"
        lines.append(f"{branch} ({commit}) -> {path}{marker}")

    show_output("Git Worktrees", lines)


def create_individual_action():
    """Create a new individual from LUCA."""
    # Check if LUCA exists
    worktrees = get_worktrees()
    luca_exists = any(w.get('branch') == 'luca' for w in worktrees)

    if not luca_exists:
        show_output("Error", [
            "LUCA worktree not found.",
            "LUCA must exist before creating new individuals.",
            "",
            "Create LUCA first using 'Create LUCA' option."
        ])
        return

    name = input_str("Individual name")
    if not name:
        return

    # Sanitize name
    name = name.strip().replace(' ', '-').lower()
    if not name:
        show_output("Error", ["Invalid name."])
        return

    # Check if already exists
    existing_branches = [w.get('branch') for w in worktrees]
    if name in existing_branches:
        show_output("Error", [f"Branch '{name}' already exists."])
        return

    path = os.path.join(INDIVIDUALS_DIR, name)
    cmd = f"git worktree add {path} -b {name} luca"
    run_command(cmd, cwd=PROJECT_ROOT)


def create_luca_action():
    """Create the LUCA worktree from main."""
    worktrees = get_worktrees()
    luca_exists = any(w.get('branch') == 'luca' for w in worktrees)

    if luca_exists:
        show_output("LUCA Exists", ["LUCA worktree already exists."])
        return

    path = os.path.join(INDIVIDUALS_DIR, "luca")
    cmd = f"git worktree add {path} -b luca HEAD"
    run_command(cmd, cwd=PROJECT_ROOT)


def delete_individual_action():
    """Delete an individual worktree."""
    individuals = get_individuals()
    if not individuals:
        show_output("No Individuals", ["No individual worktrees found."])
        return

    options = [w.get('branch', 'unknown') for w in individuals]
    options.append("Cancel")

    choice = select_menu("Select individual to delete", options, 0)
    if choice == -1 or choice == len(options) - 1:
        return

    selected = individuals[choice]
    path = selected.get('path')
    branch = selected.get('branch')

    if branch == 'luca':
        show_output("Warning", [
            "You are about to delete LUCA.",
            "This will prevent creating new individuals until LUCA is recreated.",
            "",
            "Are you sure? Delete anyway using the menu below."
        ])
        confirm = select_menu("Confirm delete LUCA?", ["No, cancel", "Yes, delete LUCA"], 0)
        if confirm != 1:
            return

    cmd = f"git worktree remove {path} && git branch -D {branch}"
    run_command(cmd, cwd=PROJECT_ROOT)


def show_path_action():
    """Show path to a worktree for navigation."""
    worktrees = get_worktrees()
    if not worktrees:
        show_output("No Worktrees", ["No worktrees found."])
        return

    options = []
    for w in worktrees:
        branch = w.get('branch', 'detached')
        options.append(branch)
    options.append("Cancel")

    choice = select_menu("Select worktree", options, 0)
    if choice == -1 or choice == len(options) - 1:
        return

    selected = worktrees[choice]
    path = selected.get('path')
    show_output("Worktree Path", [
        f"Branch: {selected.get('branch', 'detached')}",
        f"Path: {path}",
        "",
        "To navigate:",
        f"  cd {path}",
    ])


def prune_worktrees_action():
    """Prune stale worktree references."""
    run_command("git worktree prune -v", cwd=PROJECT_ROOT)


def repair_worktrees_action():
    """Repair worktree admin files."""
    run_command("git worktree repair", cwd=PROJECT_ROOT)


def sync_cli_from_main():
    """Pull CLI updates from main branch (for individuals only)."""
    show_output("Sync CLI from Main", [
        "This will fetch and checkout the cli/ folder from main branch.",
        "",
        "After sync, press R to restart CLI and apply changes.",
    ])
    run_command("git fetch origin main && git checkout origin/main -- cli/", cwd=PROJECT_ROOT)


def individuals_menu(menu_stack, initial_selected=0):
    options = [
        "List worktrees",
        "Create individual (from LUCA)",
        "Create LUCA (from main)",
        "Delete individual",
        "Show worktree path",
        "Prune stale worktrees",
        "Repair worktrees",
    ]

    selected = initial_selected
    while True:
        menu_stack[-1]['selected'] = selected
        choice = select_menu("Individuals", options, selected)

        if choice == -1:
            break
        else:
            selected = choice
            menu_stack[-1]['selected'] = selected
            if choice == 0:
                list_worktrees_action()
            elif choice == 1:
                create_individual_action()
            elif choice == 2:
                create_luca_action()
            elif choice == 3:
                delete_individual_action()
            elif choice == 4:
                show_path_action()
            elif choice == 5:
                prune_worktrees_action()
            elif choice == 6:
                repair_worktrees_action()
