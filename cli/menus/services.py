import os
from cli.core import PROJECT_ROOT, select_menu, run_command

SERVICES_DIR = os.path.join(PROJECT_ROOT, "environment", "services")
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")


def services_menu(menu_stack, initial_selected=0):
    options = [
        "Start services",
        "Stop services",
        "Restart services",
    ]

    selected = initial_selected
    while True:
        menu_stack[-1]['selected'] = selected
        choice = select_menu("Environment Services", options, selected)

        if choice == -1:
            break
        else:
            selected = choice
            menu_stack[-1]['selected'] = selected
            if choice == 0:
                run_command(f"docker compose --env-file {ENV_FILE} up -d", cwd=SERVICES_DIR)
            elif choice == 1:
                run_command(f"docker compose --env-file {ENV_FILE} down", cwd=SERVICES_DIR)
            elif choice == 2:
                run_command(f"docker compose --env-file {ENV_FILE} restart", cwd=SERVICES_DIR)
