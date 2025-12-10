# Project rules configuration

MAX_FILE_LINES = 700
MAX_FOLDER_FILES = 7
MAX_FOLDER_DEPTH = 5
MAX_CYCLOMATIC_COMPLEXITY = 10

# File extensions to analyze for code metrics
CODE_EXTENSIONS = {
    '.py',
    '.js',
    '.ts',
    '.tsx',
    '.jsx',
    '.go',
    '.rs',
    '.java',
    '.c',
    '.cpp',
    '.h',
    '.hpp',
    '.sh',
    '.yml',
    '.yaml',
    '.json',
    '.md',
    '.html',
    '.css',
    '.scss',
}

# Folders to ignore during analysis
IGNORE_FOLDERS = {
    '__pycache__',
    'node_modules',
    '.git',
    '.venv',
    'venv',
    '.idea',
    '.vscode',
}

# Files to ignore during analysis
IGNORE_FILES = {
    '.state.json',
    '.DS_Store',
}

# Secret detection patterns (regex, description)
SECRET_PATTERNS = [
    (r'(?i)password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
    (r'(?i)api[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
    (r'(?i)secret[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret key'),
    (r'(?i)auth[_-]?token\s*=\s*["\'][^"\']+["\']', 'Hardcoded auth token'),
    (r'(?i)private[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded private key'),
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub personal access token'),
    (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API key'),
]

# Files to exclude from secret scanning
SECRET_SCAN_IGNORE = {
    '.env.example',
    'config.example.py',
}
