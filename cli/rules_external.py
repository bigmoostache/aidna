"""External tool rule checks (radon, ruff, bandit)."""
import os
import json
import subprocess
import shutil
from cli.core import PROJECT_ROOT
from cli.config import MAX_CYCLOMATIC_COMPLEXITY, IGNORE_FOLDERS


EXTERNAL_TOOLS = {
    'radon': 'pip install radon',
    'ruff': 'pip install ruff',
    'bandit': 'pip install bandit',
}


def is_tool_installed(tool_name):
    """Check if an external tool is installed."""
    return shutil.which(tool_name) is not None


def get_tool_status():
    """Get installation status of all external tools."""
    return {name: is_tool_installed(name) for name in EXTERNAL_TOOLS}


def run_json_command(cmd):
    """Run a command and parse JSON output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,  # nosec B602
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.stdout.strip():
            return json.loads(result.stdout)
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return None


def check_cyclomatic_complexity():
    """Check cyclomatic complexity using radon."""
    if not is_tool_installed('radon'):
        return None

    exclude_args = ','.join(IGNORE_FOLDERS)
    cmd = f'radon cc --json --exclude "{exclude_args}" .'
    data = run_json_command(cmd)

    if data is None:
        return []

    violations = []
    for filepath, functions in data.items():
        rel_path = os.path.relpath(filepath, PROJECT_ROOT)
        for func in functions:
            complexity = func.get('complexity', 0)
            if complexity > MAX_CYCLOMATIC_COMPLEXITY:
                func_name = func.get('name', 'unknown')
                line = func.get('lineno', 0)
                rank = func.get('rank', '?')
                violations.append((rel_path, func_name, line, complexity, rank))

    return violations


def check_ruff_linting():
    """Check linting issues using ruff."""
    if not is_tool_installed('ruff'):
        return None

    exclude_args = ' '.join(f'--exclude {f}' for f in IGNORE_FOLDERS)
    cmd = f'ruff check --output-format json {exclude_args} .'
    data = run_json_command(cmd)

    if data is None:
        return []

    violations = []
    for issue in data:
        filepath = issue.get('filename', '')
        rel_path = os.path.relpath(filepath, PROJECT_ROOT) if filepath else ''
        code = issue.get('code', '')
        message = issue.get('message', '')
        location = issue.get('location', {})
        line = location.get('row', 0)
        violations.append((rel_path, line, code, message))

    return violations


def check_bandit_security():
    """Check security issues using bandit."""
    if not is_tool_installed('bandit'):
        return None

    exclude_args = ','.join(IGNORE_FOLDERS)
    cmd = f'bandit -r . -f json --exclude {exclude_args}'
    data = run_json_command(cmd)

    if data is None:
        return []

    violations = []
    results = data.get('results', [])
    for issue in results:
        severity = issue.get('issue_severity', 'LOW')
        if severity in ('HIGH', 'MEDIUM'):
            filepath = issue.get('filename', '')
            rel_path = os.path.relpath(filepath, PROJECT_ROOT) if filepath else ''
            line = issue.get('line_number', 0)
            confidence = issue.get('issue_confidence', '')
            text = issue.get('issue_text', '')
            violations.append((rel_path, line, severity, confidence, text))

    return violations
