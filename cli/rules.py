import json
import os
import re

from cli.config import (
    CODE_EXTENSIONS,
    IGNORE_EXTENSIONS,
    IGNORE_FILES,
    IGNORE_FOLDERS,
    MAX_FILE_LINES,
    MAX_FOLDER_DEPTH,
    MAX_FOLDER_FILES,
    SECRET_PATTERNS,
    SECRET_SCAN_IGNORE,
)
from cli.core import PROJECT_ROOT


def should_ignore(name, is_dir=False):
    """Check if a file/folder should be ignored."""
    if is_dir:
        return name in IGNORE_FOLDERS
    if name in IGNORE_FILES:
        return True
    _, ext = os.path.splitext(name)
    return ext.lower() in IGNORE_EXTENSIONS


def count_lines(filepath):
    """Count lines in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def get_file_size_kb(filepath):
    """Get file size in KB."""
    try:
        return round(os.path.getsize(filepath) / 1024, 2)
    except Exception:
        return 0


def is_code_file(filename):
    """Check if file has a code extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower() in CODE_EXTENSIONS


def check_file_lengths():
    """Check all files for line count violations."""
    violations = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not should_ignore(d, is_dir=True)]

        for f in files:
            if should_ignore(f):
                continue
            filepath = os.path.join(root, f)
            if is_code_file(f):
                lines = count_lines(filepath)
                if lines > MAX_FILE_LINES:
                    rel_path = os.path.relpath(filepath, PROJECT_ROOT)
                    violations.append((rel_path, lines))
    return violations


def check_folder_counts():
    """Check all folders for file count violations."""
    violations = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not should_ignore(d, is_dir=True)]

        file_count = len([f for f in files if not should_ignore(f)])
        if file_count > MAX_FOLDER_FILES:
            rel_path = os.path.relpath(root, PROJECT_ROOT)
            if rel_path == '.':
                rel_path = '(root)'
            violations.append((rel_path, file_count))
    return violations


def update_claude_json(folder_path):
    """Update claude.json in a folder with current file info."""
    claude_file = os.path.join(folder_path, 'claude.json')

    # Load existing data
    existing = {}
    if os.path.exists(claude_file):
        try:
            with open(claude_file, 'r') as f:
                existing = json.load(f)
        except Exception:
            existing = {}

    # Get current files and folders
    entries = {}
    warnings = []

    try:
        items = os.listdir(folder_path)
    except Exception:
        return [], ["Cannot read folder"]

    for item in items:
        if item == 'claude.json' or should_ignore(item):
            continue

        item_path = os.path.join(folder_path, item)
        is_dir = os.path.isdir(item_path)

        if is_dir and should_ignore(item, is_dir=True):
            continue

        entry = existing.get(item, {})

        if is_dir:
            entry['type'] = 'folder'
            entry['size_kb'] = None
            entry['lines'] = None
        else:
            entry['type'] = 'file'
            entry['size_kb'] = get_file_size_kb(item_path)
            if is_code_file(item):
                entry['lines'] = count_lines(item_path)
            else:
                entry['lines'] = None

        if not entry.get('description'):
            warnings.append(f"Missing description: {item}")
            entry['description'] = ""

        entries[item] = entry

    # Check for removed entries
    for old_key in existing:
        if old_key not in entries:
            warnings.append(f"Removed stale entry: {old_key}")

    # Write updated file
    with open(claude_file, 'w') as f:
        json.dump(entries, f, indent=2)

    return entries, warnings


def update_all_claude_json():
    """Update claude.json in all folders."""
    all_warnings = []
    updated_folders = []

    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not should_ignore(d, is_dir=True)]

        rel_path = os.path.relpath(root, PROJECT_ROOT)
        if rel_path == '.':
            rel_path = '(root)'

        entries, warnings = update_claude_json(root)
        updated_folders.append(rel_path)

        for w in warnings:
            all_warnings.append(f"{rel_path}: {w}")

    return updated_folders, all_warnings


def check_missing_claude_json():
    """Check for folders missing claude.json."""
    missing = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not should_ignore(d, is_dir=True)]

        if 'claude.json' not in files:
            rel_path = os.path.relpath(root, PROJECT_ROOT)
            if rel_path == '.':
                rel_path = '(root)'
            missing.append(rel_path)

    return missing


def check_missing_descriptions():
    """Check for entries in claude.json missing descriptions."""
    missing = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not should_ignore(d, is_dir=True)]

        claude_file = os.path.join(root, 'claude.json')
        if not os.path.exists(claude_file):
            continue

        try:
            with open(claude_file, 'r') as f:
                data = json.load(f)
        except Exception:
            continue

        rel_path = os.path.relpath(root, PROJECT_ROOT)
        if rel_path == '.':
            rel_path = '(root)'

        for name, entry in data.items():
            if not entry.get('description'):
                missing.append(f"{rel_path}: {name}")

    return missing


def check_spaces_in_filenames():
    """Check for files/folders with spaces in names."""
    violations = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not should_ignore(d, is_dir=True)]

        rel_root = os.path.relpath(root, PROJECT_ROOT)

        for d in dirs:
            if ' ' in d:
                path = os.path.join(rel_root, d) if rel_root != '.' else d
                violations.append((path, 'folder'))

        for f in files:
            if should_ignore(f):
                continue
            if ' ' in f:
                path = os.path.join(rel_root, f) if rel_root != '.' else f
                violations.append((path, 'file'))

    return violations


def check_folder_depth():
    """Check for folders exceeding maximum depth."""
    violations = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not should_ignore(d, is_dir=True)]

        rel_path = os.path.relpath(root, PROJECT_ROOT)
        if rel_path == '.':
            depth = 0
        else:
            depth = rel_path.count(os.sep) + 1

        if depth > MAX_FOLDER_DEPTH:
            violations.append((rel_path, depth))

    return violations


def check_hardcoded_secrets():
    """Check for potential hardcoded secrets in code files."""
    violations = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not should_ignore(d, is_dir=True)]

        for f in files:
            if should_ignore(f) or f in SECRET_SCAN_IGNORE:
                continue
            if not is_code_file(f):
                continue

            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    for line_num, line in enumerate(file, 1):
                        for pattern, description in SECRET_PATTERNS:
                            if re.search(pattern, line):
                                violations.append((rel_path, line_num, description))
                                break
            except Exception:
                continue

    return violations


def check_cli_synced():
    """Check if cli/ folder matches origin/main (for individuals only).

    Returns:
        None if not in individual mode or git fails
        [] if synced (no differences)
        list of changed files if out of sync
    """
    import subprocess
    from cli.config import MODE

    if MODE != 'individual':
        return None

    # Fetch latest from main
    result = subprocess.run(
        ["git", "fetch", "origin", "main"],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        return None

    # Compare cli/ with origin/main
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main", "--", "cli/"],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        return None

    changed_files = [f for f in result.stdout.strip().split('\n') if f]
    return changed_files
