import os
from cli.core import PROJECT_ROOT, select_menu, run_command

SERVICES_DIR = os.path.join(PROJECT_ROOT, "environment", "services")
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")


def get_compose_cmd():
    """Get docker compose command with env file."""
    return f"docker compose --env-file {ENV_FILE}"


def get_api_port():
    """Get the API port from running docker container."""
    import subprocess
    try:
        result = subprocess.run(
            ["docker", "port", "aidna-api", "8000"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            # Output is like "0.0.0.0:8500\n[::]:8500", take first line
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
            compose = get_compose_cmd()
            if choice == 0:
                run_command(f"{compose} logs --tail=50 api", cwd=SERVICES_DIR)
            elif choice == 1:
                run_command(f"{compose} restart api", cwd=SERVICES_DIR)
            elif choice == 2:
                port = get_api_port()
                if port:
                    run_command(f"curl -s http://localhost:{port}/", cwd=SERVICES_DIR)
                else:
                    run_command("docker port aidna-api 8000 || echo 'Container not found'", cwd=SERVICES_DIR)


def services_menu(menu_stack, initial_selected=0):
    options = [
        "Start",
        "Stop",
        "Restart",
        "Rebuild + Start",
        "FastAPI",
        "Healthcheck - Check status of all services",
        "View logs - Show last 50 lines from all containers",
        "Show config - Display resolved docker-compose config",
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
            compose = get_compose_cmd()
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
