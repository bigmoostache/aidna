import os
import json
from cli.core import PROJECT_ROOT, select_menu, show_output, show_file, input_str, input_int
from cli.config import IGNORE_FOLDERS, IGNORE_FILES

# Exploration state
_current_path = PROJECT_ROOT
_max_depth = 2


def load_claude_json(folder_path):
    """Load claude.json from a folder."""
    claude_file = os.path.join(folder_path, 'claude.json')
    if os.path.exists(claude_file):
        try:
            with open(claude_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def build_tree(path, prefix="", is_last=True, is_root=True, current_depth=0, max_depth=None):
    """Build tree with descriptions from claude.json."""
    lines = []
    name = os.path.basename(path) or "."

    if is_root:
        rel_path = os.path.relpath(path, PROJECT_ROOT)
        if rel_path == '.':
            lines.append(".")
        else:
            lines.append(f"./{rel_path}")
    else:
        connector = "└── " if is_last else "├── "
        parent_path = os.path.dirname(path)
        parent_claude = load_claude_json(parent_path)
        desc = parent_claude.get(name, {}).get('description', '')

        if desc:
            lines.append(f"{prefix}{connector}{name}  \033[90m# {desc}\033[0m")
        else:
            lines.append(f"{prefix}{connector}{name}")

    if os.path.isdir(path):
        if max_depth is not None and current_depth >= max_depth:
            try:
                items = os.listdir(path)
                sub_count = len([i for i in items if i not in IGNORE_FOLDERS and i not in IGNORE_FILES and i != 'claude.json'])
                if sub_count > 0 and not is_root:
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    lines.append(f"{new_prefix}\033[90m... ({sub_count} items)\033[0m")
            except:
                pass
            return lines

        try:
            items = os.listdir(path)
        except:
            return lines

        dirs = sorted([i for i in items if os.path.isdir(os.path.join(path, i)) and i not in IGNORE_FOLDERS and i != 'claude.json'])
        files = sorted([i for i in items if os.path.isfile(os.path.join(path, i)) and i not in IGNORE_FILES and i != 'claude.json'])

        all_items = dirs + files

        for i, item in enumerate(all_items):
            item_path = os.path.join(path, item)
            is_last_item = (i == len(all_items) - 1)

            if is_root:
                new_prefix = ""
            else:
                new_prefix = prefix + ("    " if is_last else "│   ")

            lines.extend(build_tree(item_path, new_prefix, is_last_item, is_root=False,
                                   current_depth=current_depth + 1, max_depth=max_depth))

    return lines


def show_tree():
    """Show tree with current settings."""
    global _current_path, _max_depth
    tree_lines = build_tree(_current_path, max_depth=_max_depth)

    rel_path = os.path.relpath(_current_path, PROJECT_ROOT)
    if rel_path == '.':
        rel_path = '(root)'
    depth_str = str(_max_depth) if _max_depth else '∞'
    header = [f"Path: {rel_path}  |  Depth: {depth_str}", ""]

    show_output("File Structure", header + tree_lines)


def set_path():
    """Set path via text input."""
    global _current_path

    rel_path = os.path.relpath(_current_path, PROJECT_ROOT)
    if rel_path == '.':
        rel_path = ''

    result = input_str("Path (relative to root, empty=root)", rel_path)
    if result is None:
        return

    if result == '' or result == '.':
        _current_path = PROJECT_ROOT
    elif result == '..':
        if _current_path != PROJECT_ROOT:
            _current_path = os.path.dirname(_current_path)
    else:
        # Handle relative path
        new_path = os.path.normpath(os.path.join(PROJECT_ROOT, result))
        # Ensure it's within project root
        if new_path.startswith(PROJECT_ROOT) and os.path.isdir(new_path):
            _current_path = new_path


def set_depth():
    """Set depth via text input."""
    global _max_depth

    current = str(_max_depth) if _max_depth else "0"
    result = input_int("Depth (0=unlimited)", int(current) if current != "0" else 0, min_val=0, max_val=99)

    if result is not None:
        _max_depth = result if result > 0 else None


def find_claude_md_files():
    """Find all CLAUDE.md files in the project with their descriptions."""
    claude_files = []

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Filter ignored folders
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        if 'CLAUDE.md' in files:
            claude_path = os.path.join(root, 'CLAUDE.md')
            rel_path = os.path.relpath(root, PROJECT_ROOT)
            if rel_path == '.':
                rel_path = '(root)'
                display_path = 'CLAUDE.md'
            else:
                display_path = os.path.join(rel_path, 'CLAUDE.md')

            # Get description from claude.json in same folder
            claude_json = load_claude_json(root)
            description = claude_json.get('CLAUDE.md', {}).get('description', '')

            claude_files.append({
                'path': claude_path,
                'rel_path': rel_path,
                'display_path': display_path,
                'description': description,
            })

    # Sort: root first, then alphabetically
    claude_files.sort(key=lambda x: (x['rel_path'] != '(root)', x['rel_path']))
    return claude_files


def find_parent_claude_md(folder_path):
    """Find parent CLAUDE.md files (from parent folders up to project root)."""
    parents = []
    current = os.path.dirname(folder_path)

    while current.startswith(PROJECT_ROOT) and current != PROJECT_ROOT:
        claude_path = os.path.join(current, 'CLAUDE.md')
        if os.path.exists(claude_path):
            rel_path = os.path.relpath(current, PROJECT_ROOT)
            claude_json = load_claude_json(current)
            description = claude_json.get('CLAUDE.md', {}).get('description', '')
            parents.append({
                'path': claude_path,
                'rel_path': rel_path,
                'description': description,
            })
        current = os.path.dirname(current)

    # Check project root
    root_claude = os.path.join(PROJECT_ROOT, 'CLAUDE.md')
    if os.path.exists(root_claude) and folder_path != PROJECT_ROOT:
        claude_json = load_claude_json(PROJECT_ROOT)
        description = claude_json.get('CLAUDE.md', {}).get('description', '')
        parents.append({
            'path': root_claude,
            'rel_path': '(root)',
            'description': description,
        })

    # Reverse so root is first
    parents.reverse()
    return parents


def find_children_claude_md(folder_path):
    """Find children CLAUDE.md files (in subdirectories)."""
    children = []

    for root, dirs, files in os.walk(folder_path):
        # Skip the current folder itself
        if root == folder_path:
            dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]
            continue

        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        if 'CLAUDE.md' in files:
            claude_path = os.path.join(root, 'CLAUDE.md')
            rel_path = os.path.relpath(root, PROJECT_ROOT)
            claude_json = load_claude_json(root)
            description = claude_json.get('CLAUDE.md', {}).get('description', '')
            children.append({
                'path': claude_path,
                'rel_path': rel_path,
                'description': description,
            })

    # Sort alphabetically
    children.sort(key=lambda x: x['rel_path'])
    return children


def show_claude_md_with_context(title, file_path, folder_path):
    """Display CLAUDE.md with parent and children context."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        show_output(title, [f"\033[31mError reading file: {e}\033[0m"])
        return

    from cli.core import clear_screen, get_key

    clear_screen()

    # Find parents and children
    parents = find_parent_claude_md(folder_path)
    children = find_children_claude_md(folder_path)

    # Print parents section
    if parents:
        print("\033[90m" + "─" * 60 + "\033[0m")
        print("\033[1;90mParent CLAUDE.md files:\033[0m")
        for p in parents:
            if p['description']:
                print(f"  \033[90m↑ {p['rel_path']}/CLAUDE.md  # {p['description']}\033[0m")
            else:
                print(f"  \033[90m↑ {p['rel_path']}/CLAUDE.md\033[0m")
        print("\033[90m" + "─" * 60 + "\033[0m")
        print()

    # Print main file
    print(f"\033[1m{title}\033[0m")
    print(f"\033[90m{file_path}\033[0m")
    print()
    print(content)

    # Print children section
    if children:
        print()
        print("\033[90m" + "─" * 60 + "\033[0m")
        print("\033[1;90mChildren CLAUDE.md files:\033[0m")
        for c in children:
            if c['description']:
                print(f"  \033[90m↓ {c['rel_path']}/CLAUDE.md  # {c['description']}\033[0m")
            else:
                print(f"  \033[90m↓ {c['rel_path']}/CLAUDE.md\033[0m")
        print("\033[90m" + "─" * 60 + "\033[0m")

    print("\nPress any key to continue...")
    get_key()


def claude_md_menu(menu_stack, initial_selected=0):
    """Menu to browse and view CLAUDE.md files."""
    claude_files = find_claude_md_files()

    if not claude_files:
        show_output("CLAUDE.md Explorer", ["\033[33mNo CLAUDE.md files found in project.\033[0m"])
        return

    selected = initial_selected
    while True:
        # Build menu options with descriptions
        options = []
        for cf in claude_files:
            if cf['description']:
                options.append(f"{cf['display_path']}  \033[90m# {cf['description']}\033[0m")
            else:
                options.append(cf['display_path'])

        menu_stack[-1]['selected'] = selected
        choice = select_menu(f"CLAUDE.md Files ({len(claude_files)})", options, selected)

        if choice == -1:
            break
        else:
            selected = choice
            menu_stack[-1]['selected'] = selected
            # Show the selected file with context
            cf = claude_files[choice]
            folder_path = os.path.dirname(cf['path'])
            show_claude_md_with_context(f"CLAUDE.md - {cf['rel_path']}", cf['path'], folder_path)


def exploration_menu(menu_stack, initial_selected=0):
    global _current_path, _max_depth

    selected = initial_selected
    while True:
        rel_path = os.path.relpath(_current_path, PROJECT_ROOT)
        if rel_path == '.':
            rel_path = '(root)'
        depth_str = str(_max_depth) if _max_depth else '∞'

        options = [
            f"Show file structure",
            f"CLAUDE.md explorer",
            f"Set path [{rel_path}]",
            f"Set depth [{depth_str}]",
        ]

        menu_stack[-1]['selected'] = selected
        choice = select_menu("Exploration", options, selected)

        if choice == -1:
            break
        else:
            selected = choice
            menu_stack[-1]['selected'] = selected
            if choice == 0:
                show_tree()
            elif choice == 1:
                menu_stack.append({'menu': 'claude_md', 'selected': 0})
                claude_md_menu(menu_stack)
                menu_stack.pop()
            elif choice == 2:
                set_path()
            elif choice == 3:
                set_depth()
