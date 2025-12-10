from cli.core import select_menu, show_output
from cli.config import (
    MAX_FILE_LINES, MAX_FOLDER_FILES, MAX_FOLDER_DEPTH, MAX_CYCLOMATIC_COMPLEXITY
)
from cli.rules import (
    check_file_lengths, check_folder_counts,
    update_all_claude_json, check_missing_claude_json, check_missing_descriptions,
    check_spaces_in_filenames, check_folder_depth, check_hardcoded_secrets
)
from cli.rules_external import (
    check_cyclomatic_complexity, check_ruff_linting, check_bandit_security,
    get_tool_status, EXTERNAL_TOOLS
)


def rules_menu(menu_stack, initial_selected=0):
    options = [
        "Run all checks",
        "Individual checks",
        "Update claude.json files",
        "External tool status",
    ]

    selected = initial_selected
    while True:
        menu_stack[-1]['selected'] = selected
        choice = select_menu("Project Rules", options, selected)

        if choice == -1:
            break
        else:
            selected = choice
            menu_stack[-1]['selected'] = selected

            if choice == 0:
                _check_all_rules()
            elif choice == 1:
                menu_stack.append({'menu': 'individual_checks', 'selected': 0})
                _individual_checks_menu(menu_stack)
                menu_stack.pop()
            elif choice == 2:
                _update_claude_json()
            elif choice == 3:
                _show_tool_status()


def _individual_checks_menu(menu_stack, initial_selected=0):
    options = [
        "Check file lengths",
        "Check folder file counts",
        "Check spaces in filenames",
        "Check folder depth",
        "Check hardcoded secrets",
        "Check cyclomatic complexity",
        "Check linting issues",
        "Check security issues",
        "Check missing claude.json",
        "Check missing descriptions",
    ]

    selected = initial_selected
    while True:
        menu_stack[-1]['selected'] = selected
        choice = select_menu("Individual Checks", options, selected)

        if choice == -1:
            break
        else:
            selected = choice
            menu_stack[-1]['selected'] = selected

            if choice == 0:
                _check_file_lengths()
            elif choice == 1:
                _check_folder_counts()
            elif choice == 2:
                _check_spaces_in_filenames()
            elif choice == 3:
                _check_folder_depth()
            elif choice == 4:
                _check_hardcoded_secrets()
            elif choice == 5:
                _check_cyclomatic_complexity()
            elif choice == 6:
                _check_ruff_linting()
            elif choice == 7:
                _check_bandit_security()
            elif choice == 8:
                _check_missing_claude_json()
            elif choice == 9:
                _check_missing_descriptions()


def _check_file_lengths():
    violations = check_file_lengths()
    if violations:
        lines = [f"\033[31mFiles exceeding {MAX_FILE_LINES} lines:\033[0m", ""]
        for path, count in violations:
            lines.append(f"  {path}: {count} lines")
    else:
        lines = [f"\033[32mAll files are under {MAX_FILE_LINES} lines.\033[0m"]
    show_output("File Length Check", lines)


def _check_folder_counts():
    violations = check_folder_counts()
    if violations:
        lines = [f"\033[31mFolders exceeding {MAX_FOLDER_FILES} files:\033[0m", ""]
        for path, count in violations:
            lines.append(f"  {path}: {count} files")
    else:
        lines = [f"\033[32mAll folders have {MAX_FOLDER_FILES} or fewer files.\033[0m"]
    show_output("Folder Count Check", lines)


def _check_spaces_in_filenames():
    violations = check_spaces_in_filenames()
    if violations:
        lines = ["\033[31mFiles/folders with spaces in names:\033[0m", ""]
        for path, item_type in violations:
            lines.append(f"  {path} ({item_type})")
    else:
        lines = ["\033[32mNo files or folders have spaces in names.\033[0m"]
    show_output("Spaces in Filenames Check", lines)


def _check_folder_depth():
    violations = check_folder_depth()
    if violations:
        lines = [f"\033[31mFolders exceeding {MAX_FOLDER_DEPTH} levels deep:\033[0m", ""]
        for path, depth in violations:
            lines.append(f"  {path}: depth {depth}")
    else:
        lines = [f"\033[32mAll folders are within {MAX_FOLDER_DEPTH} levels deep.\033[0m"]
    show_output("Folder Depth Check", lines)


def _check_hardcoded_secrets():
    violations = check_hardcoded_secrets()
    if violations:
        lines = ["\033[31mPotential hardcoded secrets found:\033[0m", ""]
        for path, line_num, description in violations:
            lines.append(f"  {path}:{line_num} - {description}")
    else:
        lines = ["\033[32mNo hardcoded secrets detected.\033[0m"]
    show_output("Hardcoded Secrets Check", lines)


def _check_cyclomatic_complexity():
    violations = check_cyclomatic_complexity()
    if violations is None:
        lines = ["\033[33mRadon is not installed.\033[0m", "",
                 "Install with: pip install radon"]
    elif violations:
        lines = [f"\033[31mFunctions exceeding complexity {MAX_CYCLOMATIC_COMPLEXITY}:\033[0m", ""]
        for path, func, line, cc, rank in violations:
            lines.append(f"  {path}:{line} {func}() - CC={cc} (rank {rank})")
    else:
        lines = [f"\033[32mAll functions have acceptable complexity (≤ {MAX_CYCLOMATIC_COMPLEXITY}).\033[0m"]
    show_output("Cyclomatic Complexity Check", lines)


def _check_ruff_linting():
    violations = check_ruff_linting()
    if violations is None:
        lines = ["\033[33mRuff is not installed.\033[0m", "",
                 "Install with: pip install ruff"]
    elif violations:
        lines = [f"\033[31mLinting issues found ({len(violations)}):\033[0m", ""]
        for path, line, code, message in violations[:20]:
            lines.append(f"  {path}:{line} [{code}] {message}")
        if len(violations) > 20:
            lines.append(f"  ... and {len(violations) - 20} more")
    else:
        lines = ["\033[32mNo linting issues found.\033[0m"]
    show_output("Linting Check (ruff)", lines)


def _check_bandit_security():
    violations = check_bandit_security()
    if violations is None:
        lines = ["\033[33mBandit is not installed.\033[0m", "",
                 "Install with: pip install bandit"]
    elif violations:
        lines = [f"\033[31mSecurity issues found ({len(violations)}):\033[0m", ""]
        for path, line, severity, confidence, text in violations:
            color = '\033[31m' if severity == 'HIGH' else '\033[33m'
            lines.append(f"  {color}[{severity}]\033[0m {path}:{line} - {text}")
    else:
        lines = ["\033[32mNo high/medium security issues found.\033[0m"]
    show_output("Security Check (bandit)", lines)


def _check_missing_claude_json():
    missing = check_missing_claude_json()
    if missing:
        lines = ["\033[33mFolders missing claude.json:\033[0m", ""]
        for path in missing:
            lines.append(f"  {path}")
    else:
        lines = ["\033[32mAll folders have claude.json.\033[0m"]
    show_output("Missing claude.json Check", lines)


def _check_missing_descriptions():
    missing = check_missing_descriptions()
    if missing:
        lines = ["\033[33mEntries missing descriptions:\033[0m", ""]
        for item in missing:
            lines.append(f"  {item}")
    else:
        lines = ["\033[32mAll entries have descriptions.\033[0m"]
    show_output("Missing Descriptions Check", lines)


def _check_all_rules():
    lines = []

    # File lengths
    file_violations = check_file_lengths()
    if file_violations:
        lines.append(f"\033[31mFiles exceeding {MAX_FILE_LINES} lines:\033[0m")
        for path, count in file_violations:
            lines.append(f"  {path}: {count} lines")
        lines.append("")
    else:
        lines.append(f"\033[32m✓ All files under {MAX_FILE_LINES} lines\033[0m")

    # Folder counts
    folder_violations = check_folder_counts()
    if folder_violations:
        lines.append(f"\033[31mFolders exceeding {MAX_FOLDER_FILES} files:\033[0m")
        for path, count in folder_violations:
            lines.append(f"  {path}: {count} files")
        lines.append("")
    else:
        lines.append(f"\033[32m✓ All folders have {MAX_FOLDER_FILES} or fewer files\033[0m")

    # Spaces in filenames
    spaces_violations = check_spaces_in_filenames()
    if spaces_violations:
        lines.append(f"\033[31mFiles/folders with spaces ({len(spaces_violations)}):\033[0m")
        for path, item_type in spaces_violations[:5]:
            lines.append(f"  {path}")
        if len(spaces_violations) > 5:
            lines.append(f"  ... and {len(spaces_violations) - 5} more")
        lines.append("")
    else:
        lines.append(f"\033[32m✓ No spaces in filenames\033[0m")

    # Folder depth
    depth_violations = check_folder_depth()
    if depth_violations:
        lines.append(f"\033[31mFolders too deep ({len(depth_violations)}):\033[0m")
        for path, depth in depth_violations[:5]:
            lines.append(f"  {path}: depth {depth}")
        lines.append("")
    else:
        lines.append(f"\033[32m✓ All folders within depth limit\033[0m")

    # Hardcoded secrets
    secret_violations = check_hardcoded_secrets()
    if secret_violations:
        lines.append(f"\033[31mPotential secrets ({len(secret_violations)}):\033[0m")
        for path, line_num, desc in secret_violations[:5]:
            lines.append(f"  {path}:{line_num}")
        lines.append("")
    else:
        lines.append(f"\033[32m✓ No hardcoded secrets detected\033[0m")

    # Missing claude.json
    missing = check_missing_claude_json()
    if missing:
        lines.append(f"\033[33mFolders missing claude.json:\033[0m")
        for path in missing:
            lines.append(f"  {path}")
        lines.append("")
    else:
        lines.append(f"\033[32m✓ All folders have claude.json\033[0m")

    # Missing descriptions
    missing_desc = check_missing_descriptions()
    if missing_desc:
        lines.append(f"\033[33mMissing descriptions in claude.json:\033[0m")
        for item in missing_desc:
            lines.append(f"  {item}")
        lines.append("")
    else:
        lines.append(f"\033[32m✓ All entries have descriptions\033[0m")

    # External tool checks (graceful degradation)
    cc_violations = check_cyclomatic_complexity()
    if cc_violations is None:
        lines.append(f"\033[33m⚠ Complexity check skipped (radon not installed)\033[0m")
    elif cc_violations:
        lines.append(f"\033[31mHigh complexity functions ({len(cc_violations)}):\033[0m")
        for path, func, line, cc, rank in cc_violations[:3]:
            lines.append(f"  {path}:{line} {func}() CC={cc}")
        lines.append("")
    else:
        lines.append(f"\033[32m✓ All functions have acceptable complexity\033[0m")

    ruff_violations = check_ruff_linting()
    if ruff_violations is None:
        lines.append(f"\033[33m⚠ Linting check skipped (ruff not installed)\033[0m")
    elif ruff_violations:
        lines.append(f"\033[31mLinting issues ({len(ruff_violations)})\033[0m")
    else:
        lines.append(f"\033[32m✓ No linting issues\033[0m")

    bandit_violations = check_bandit_security()
    if bandit_violations is None:
        lines.append(f"\033[33m⚠ Security check skipped (bandit not installed)\033[0m")
    elif bandit_violations:
        lines.append(f"\033[31mSecurity issues ({len(bandit_violations)})\033[0m")
    else:
        lines.append(f"\033[32m✓ No security issues\033[0m")

    show_output("All Rules Check", lines)


def _update_claude_json():
    folders, warnings = update_all_claude_json()
    lines = [f"Updated {len(folders)} folders.", ""]

    if warnings:
        lines.append("\033[33mWarnings:\033[0m")
        for w in warnings:
            lines.append(f"  {w}")
    else:
        lines.append("\033[32mNo warnings.\033[0m")

    show_output("Update claude.json", lines)


def _show_tool_status():
    status = get_tool_status()
    lines = ["External tool installation status:", ""]
    for tool, installed in status.items():
        if installed:
            lines.append(f"  \033[32m✓ {tool}: Installed\033[0m")
        else:
            install_cmd = EXTERNAL_TOOLS[tool]
            lines.append(f"  \033[31m✗ {tool}: Not installed\033[0m")
            lines.append(f"      Install with: {install_cmd}")
    show_output("External Tool Status", lines)
