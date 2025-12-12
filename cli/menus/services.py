import os

from cli.core import PROJECT_ROOT, run_command, select_menu

BODY_DIR = os.path.join(PROJECT_ROOT, "body")
MIND_DIR = os.path.join(PROJECT_ROOT, "mind")
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")


def get_compose_cmd():
    """Get docker compose command with env file."""
    return f"docker compose --env-file {ENV_FILE}"


def body_menu(menu_stack):
    options = [
        "Start",
        "Stop",
        "Rebuild + Start",
        "Logs",
        "Healthcheck",
    ]

    menu_stack.append({'menu': 'body', 'selected': 0})
    selected = 0
    while True:
        menu_stack[-1]['selected'] = selected
        choice = select_menu("Body Service", options, selected)

        if choice == -1:
            menu_stack.pop()
            break
        else:
            selected = choice
            compose = get_compose_cmd()
            if choice == 0:
                run_command(f"{compose} up -d", cwd=BODY_DIR)
            elif choice == 1:
                run_command(f"{compose} down", cwd=BODY_DIR)
            elif choice == 2:
                run_command(f"{compose} up -d --build", cwd=BODY_DIR)
            elif choice == 3:
                run_command(f"{compose} logs --tail=50", cwd=BODY_DIR)
            elif choice == 4:
                run_command("curl -s http://localhost:8501/health || echo 'Body not responding'", cwd=BODY_DIR)


def mind_menu(menu_stack):
    options = [
        "Start",
        "Stop",
        "Rebuild + Start",
        "Logs",
        "Follow logs",
    ]

    menu_stack.append({'menu': 'mind', 'selected': 0})
    selected = 0
    while True:
        menu_stack[-1]['selected'] = selected
        choice = select_menu("Mind Service", options, selected)

        if choice == -1:
            menu_stack.pop()
            break
        else:
            selected = choice
            compose = get_compose_cmd()
            if choice == 0:
                run_command(f"{compose} up -d", cwd=MIND_DIR)
            elif choice == 1:
                run_command(f"{compose} down", cwd=MIND_DIR)
            elif choice == 2:
                run_command(f"{compose} up -d --build", cwd=MIND_DIR)
            elif choice == 3:
                run_command(f"{compose} logs --tail=50", cwd=MIND_DIR)
            elif choice == 4:
                run_command(f"{compose} logs -f", cwd=MIND_DIR)


def services_menu(menu_stack, initial_selected=0):
    options = [
        "Body",
        "Mind",
    ]

    selected = initial_selected
    while True:
        menu_stack[-1]['selected'] = selected
        choice = select_menu("Services", options, selected)

        if choice == -1:
            break
        else:
            selected = choice
            menu_stack[-1]['selected'] = selected
            if choice == 0:
                body_menu(menu_stack)
            elif choice == 1:
                mind_menu(menu_stack)
