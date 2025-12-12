#!/usr/bin/env python3
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.core import (
    STATE_FILE,
    GoToRoot,
    RestartRequested,
    clear_screen,
    load_state,
    save_state,
    select_menu,
)
from cli.menus import (
    claude_md_menu,
    exploration_menu,
    individual_checks_menu,
    individuals_menu,
    rules_menu,
    services_menu,
)


def main_menu(menu_stack, initial_selected=0):
    options = [
        "Services",
        "Individuals",
        "Exploration",
        "Project rules",
        "Exit",
    ]

    selected = initial_selected
    while True:
        menu_stack[-1]['selected'] = selected
        choice = select_menu("Project CLI", options, selected)

        if choice == -1:  # Back from root = Restart
            raise RestartRequested()
        elif choice == 4:  # Exit
            clear_screen()
            break
        else:
            selected = choice
            menu_stack[-1]['selected'] = selected
            if choice == 0:
                menu_stack.append({'menu': 'services', 'selected': 0})
                services_menu(menu_stack)
                menu_stack.pop()
            elif choice == 1:
                menu_stack.append({'menu': 'individuals', 'selected': 0})
                individuals_menu(menu_stack)
                menu_stack.pop()
            elif choice == 2:
                menu_stack.append({'menu': 'exploration', 'selected': 0})
                exploration_menu(menu_stack)
                menu_stack.pop()
            elif choice == 3:
                menu_stack.append({'menu': 'rules', 'selected': 0})
                rules_menu(menu_stack)
                menu_stack.pop()


def run_from_state(state):
    menu_stack = [{'menu': 'main', 'selected': 0}]

    if state:
        menu_stack = state

    current = menu_stack[-1]

    if current['menu'] == 'main':
        main_menu(menu_stack, current.get('selected', 0))
    elif current['menu'] == 'services':
        services_menu(menu_stack, current.get('selected', 0))
        menu_stack.pop()
        if menu_stack:
            main_menu(menu_stack, menu_stack[-1].get('selected', 0))
    elif current['menu'] == 'exploration':
        exploration_menu(menu_stack, current.get('selected', 0))
        menu_stack.pop()
        if menu_stack:
            main_menu(menu_stack, menu_stack[-1].get('selected', 0))
    elif current['menu'] == 'rules':
        rules_menu(menu_stack, current.get('selected', 0))
        menu_stack.pop()
        if menu_stack:
            main_menu(menu_stack, menu_stack[-1].get('selected', 0))
    elif current['menu'] == 'individuals':
        individuals_menu(menu_stack, current.get('selected', 0))
        menu_stack.pop()
        if menu_stack:
            main_menu(menu_stack, menu_stack[-1].get('selected', 0))
    elif current['menu'] == 'claude_md':
        claude_md_menu(menu_stack, current.get('selected', 0))
        menu_stack.pop()
        if menu_stack:
            run_from_state(menu_stack)
    elif current['menu'] == 'individual_checks':
        individual_checks_menu(menu_stack, current.get('selected', 0))
        menu_stack.pop()
        if menu_stack:
            run_from_state(menu_stack)

    return menu_stack


def main():
    state = load_state()
    menu_stack = [{'menu': 'main', 'selected': 0}]

    if state:
        menu_stack = state

    while True:
        try:
            run_from_state(menu_stack)
            break
        except RestartRequested:
            save_state(menu_stack)
            # Exit with code 42 to signal restart (shell will restart us)
            sys.exit(42)
        except GoToRoot:
            # Reset to main menu and continue
            menu_stack = [{'menu': 'main', 'selected': 0}]


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
