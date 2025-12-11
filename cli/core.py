#!/usr/bin/env python3
import os
import sys
import subprocess
import tty
import termios
import json
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(PROJECT_ROOT, "cli", ".state.json")


class RestartRequested(Exception):
    pass


class GoToRoot(Exception):
    pass


def save_state(menu_stack):
    with open(STATE_FILE, 'w') as f:
        json.dump(menu_stack, f)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        os.remove(STATE_FILE)
        return state
    return None


def get_key():
    """Read a single keypress."""
    import select
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            # Check if more chars available (escape sequence) or just Escape
            if select.select([sys.stdin], [], [], 0.05)[0]:
                ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def get_terminal_size():
    size = shutil.get_terminal_size((80, 24))
    return size.columns, size.lines


def clear_screen():
    """Clear screen by overwriting all lines with spaces."""
    cols, lines = get_terminal_size()
    sys.stdout.write("\033[H")
    for _ in range(lines):
        sys.stdout.write(" " * cols + "\n")
    sys.stdout.write("\033[H")
    sys.stdout.flush()


def get_menu_key(index):
    """Get display key for menu item: a-z."""
    return chr(ord('a') + index)


def render_menu(title, options, selected):
    cols, lines = get_terminal_size()
    sys.stdout.write("\033[H")

    output_lines = []
    output_lines.append(f"\033[1m{title}\033[0m")
    output_lines.append("")
    for i, option in enumerate(options):
        key = get_menu_key(i)
        if i == selected:
            output_lines.append(f"  \033[7m> [{key}] {option}\033[0m")
        else:
            output_lines.append(f"    [{key}] {option}")
    output_lines.append("")
    output_lines.append("[a-z] Select  [~] Root  [B] Back  [R] Restart")

    for line in output_lines:
        sys.stdout.write(f"{line}\033[K\n")

    remaining = lines - len(output_lines) - 1
    for _ in range(remaining):
        sys.stdout.write("\033[K\n")

    sys.stdout.flush()


def select_menu(title, options, initial_selected=0):
    """Display menu and return selected index, or -1 if quit."""
    selected = initial_selected
    while True:
        render_menu(title, options, selected)
        key = get_key()

        if key == '\x1b[A':
            selected = (selected - 1) % len(options)
        elif key == '\x1b[B':
            selected = (selected + 1) % len(options)
        elif key in ('\r', '\n'):
            return selected
        elif key == 'B':  # Back
            return -1
        elif key == 'R':  # Restart
            raise RestartRequested()
        elif key == '~':  # Go to root
            raise GoToRoot()
        elif key in 'abcdefghijklmnopqrstuvwxyz':
            idx = ord(key) - ord('a')
            if idx < len(options):
                return idx


def run_command(cmd, cwd=None):
    """Run a command and wait for keypress."""
    clear_screen()
    print("\033[1mRunning...\033[0m\n")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    print(f"\n\033[{'32' if result.returncode == 0 else '31'}m")
    print(f"{'Done!' if result.returncode == 0 else f'Failed (exit code {result.returncode})'}")
    print("\033[0m\nPress any key to continue...")
    get_key()


def show_output(title, lines_out):
    """Show output and wait for keypress."""
    clear_screen()
    print(f"\033[1m{title}\033[0m\n")
    for line in lines_out:
        print(line)
    print("\nPress any key to continue...")
    get_key()


def show_file(title, file_path):
    """Display file contents and wait for keypress."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        show_output(title, [f"\033[31mError reading file: {e}\033[0m"])
        return

    clear_screen()
    print(f"\033[1m{title}\033[0m")
    print(f"\033[90m{file_path}\033[0m")
    print()
    print(content)
    print("\nPress any key to continue...")
    get_key()


def input_str(prompt, default=""):
    """Get string input from user. Returns None if cancelled."""
    value = default
    cursor_pos = len(value)
    select_all = bool(default)  # Select all if there's a default

    while True:
        cols, lines = get_terminal_size()
        sys.stdout.write("\033[H")

        # Render with selection highlight if select_all
        if select_all and value:
            input_display = f"{prompt}: \033[7m{value}\033[0m"
        else:
            input_display = f"{prompt}: {value[:cursor_pos]}\033[7m{value[cursor_pos:cursor_pos+1] or ' '}\033[0m{value[cursor_pos+1:]}"

        output_lines = [
            "\033[1mInput\033[0m",
            "",
            input_display,
            "",
            "[Enter] Confirm  [Esc/q] Cancel  [Backspace] Delete"
        ]

        for line in output_lines:
            sys.stdout.write(f"{line}\033[K\n")

        remaining = lines - len(output_lines) - 1
        for _ in range(remaining):
            sys.stdout.write("\033[K\n")

        sys.stdout.flush()

        key = get_key()

        if key in ('\r', '\n'):
            return value
        elif key in ('\x1b', 'q', 'Q') and not value:
            return None
        elif key == '\x1b':
            return None
        elif key == '\x7f' or key == '\x08':  # Backspace
            if select_all:
                value = ""
                cursor_pos = 0
                select_all = False
            elif cursor_pos > 0:
                value = value[:cursor_pos-1] + value[cursor_pos:]
                cursor_pos -= 1
        elif key == '\x1b[D':  # Left arrow
            select_all = False
            if cursor_pos > 0:
                cursor_pos -= 1
        elif key == '\x1b[C':  # Right arrow
            select_all = False
            if cursor_pos < len(value):
                cursor_pos += 1
        elif key == '\x1b[H':  # Home
            select_all = False
            cursor_pos = 0
        elif key == '\x1b[F':  # End
            select_all = False
            cursor_pos = len(value)
        elif len(key) == 1 and key.isprintable():
            if select_all:
                value = key
                cursor_pos = 1
                select_all = False
            else:
                value = value[:cursor_pos] + key + value[cursor_pos:]
                cursor_pos += 1


def input_int(prompt, default=None, min_val=None, max_val=None):
    """Get integer input from user. Returns None if cancelled."""
    default_str = str(default) if default is not None else ""
    result = input_str(prompt, default_str)

    if result is None:
        return None

    try:
        val = int(result)
        if min_val is not None and val < min_val:
            return min_val
        if max_val is not None and val > max_val:
            return max_val
        return val
    except ValueError:
        return default
