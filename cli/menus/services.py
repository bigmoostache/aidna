import os

from cli.config import MODE, PROJECT_ROOT
from cli.core import run_command, select_menu

ENV_FILE = os.path.join(PROJECT_ROOT, ".env")

# =============================================================================
# ENVIRONMENT MODE - FastAPI + Postgres services
# =============================================================================

SERVICES_DIR = os.path.join(PROJECT_ROOT, "environment", "services")


def _get_env_compose_cmd():
    """Get docker compose command with env file for environment."""
    return f"docker compose --env-file {ENV_FILE}"


def _get_api_port():
    """Get the API port from running docker container."""
    import subprocess
    try:
        result = subprocess.run(
            ["docker", "port", "aidna-api", "8000"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            first_line = result.stdout.strip().split("\n")[0]
            port = first_line.split(":")[-1]
            return port
    except Exception:
        pass
    return None


def fastapi_menu(menu_stack):
    options = [
        "Logs",
        "Restart",
        "Healthcheck - Curl endpoint to verify service is responding",
    ]

    menu_stack.append({'menu': 'fastapi', 'selected': 0})
    selected = 0
    while True:
        menu_stack[-1]['selected'] = selected
        choice = select_menu("FastAPI Service", options, selected)

        if choice == -1:
            menu_stack.pop()
            break
        else:
            selected = choice
            compose = _get_env_compose_cmd()
            if choice == 0:
                run_command(f"{compose} logs --tail=50 api", cwd=SERVICES_DIR)
            elif choice == 1:
                run_command(f"{compose} restart api", cwd=SERVICES_DIR)
            elif choice == 2:
                port = _get_api_port()
                if port:
                    run_command(f"curl -s http://localhost:{port}/", cwd=SERVICES_DIR)
                else:
                    run_command("docker port aidna-api 8000 || echo 'Container not found'", cwd=SERVICES_DIR)


def _env_services_menu(menu_stack, initial_selected=0):
    options = [
        "Start",
        "Stop",
        "Restart",
        "Rebuild + Start",
        "FastAPI",
        "Healthcheck - Check status of all services",
        "View logs - Show last 50 lines from all containers",
        "Show config - Display resolved docker-compose config",
        "Reset DB - Stop and remove postgres volume",
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
            compose = _get_env_compose_cmd()
            if choice == 0:
                run_command(f"{compose} up -d", cwd=SERVICES_DIR)
            elif choice == 1:
                run_command(f"{compose} down", cwd=SERVICES_DIR)
            elif choice == 2:
                run_command(f"{compose} restart", cwd=SERVICES_DIR)
            elif choice == 3:
                run_command(f"{compose} up -d --build", cwd=SERVICES_DIR)
            elif choice == 4:
                fastapi_menu(menu_stack)
            elif choice == 5:
                run_command(f"{compose} ps", cwd=SERVICES_DIR)
            elif choice == 6:
                run_command(f"{compose} logs --tail=50", cwd=SERVICES_DIR)
            elif choice == 7:
                run_command(f"echo 'Command: {compose} config' && {compose} config", cwd=SERVICES_DIR)
            elif choice == 8:
                run_command(f"{compose} down -v", cwd=SERVICES_DIR)


# =============================================================================
# INDIVIDUAL MODE - Body + Mind services
# =============================================================================

BODY_DIR = os.path.join(PROJECT_ROOT, "body")
MIND_DIR = os.path.join(PROJECT_ROOT, "mind")


def _get_ind_compose_cmd():
    """Get docker compose command with env file for individual."""
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
            compose = _get_ind_compose_cmd()
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
            compose = _get_ind_compose_cmd()
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


def _individual_services_menu(menu_stack, initial_selected=0):
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


# =============================================================================
# DISPATCHER - Routes to correct menu based on MODE
# =============================================================================

def services_menu(menu_stack, initial_selected=0):
    if MODE == 'environment':
        _env_services_menu(menu_stack, initial_selected)
    else:
        _individual_services_menu(menu_stack, initial_selected)
