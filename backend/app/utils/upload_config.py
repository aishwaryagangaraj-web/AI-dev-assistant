import os
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = [".py", ".js", ".ts", ".java", ".cpp", ".txt"]

ALLOWED_MIME_TYPES = {
    ".py": [
        "text/x-python",
        "application/x-python-code",
        "text/plain",
        "application/octet-stream",
    ],
    ".js": [
        "application/javascript",
        "text/javascript",
        "text/plain",
    ],
    ".ts": [
        "application/typescript",
        "text/typescript",
        "application/x-typescript",
        "video/mp2t",
        "text/plain",
    ],
    ".java": [
        "text/x-java-source",
        "text/java",
        "application/java",
        "text/plain",
        "application/octet-stream",
    ],
    ".cpp": [
        "text/x-c++src",
        "text/x-c",
        "application/x-c++",
        "text/x-csrc",
        "application/x-cplusplus",
        "text/plain",
        "application/octet-stream",
    ],
    ".txt": [
        "text/plain",
    ],
}

BLOCKED_EXTENSIONS = [
    ".exe",
    ".bat",
    ".cmd",
    ".sh",
    ".ps1",
    ".dll",
    ".scr",
    ".msi",
    ".apk",
]

def _load_max_file_size() -> int:
    """Loads and validates max file size from env, returning bytes."""
    env_val = os.getenv("MAX_FILE_SIZE_MB", "5")
    try:
        size_mb = int(env_val)
        if size_mb <= 0:
            raise ValueError(f"MAX_FILE_SIZE_MB must be positive. Got: {size_mb}")
        return size_mb * 1024 * 1024
    except ValueError as exc:
        logger.error("Configuration error for MAX_FILE_SIZE_MB: %s", exc)
        raise ValueError(f"Invalid upload configuration: {exc}") from exc

max_file_size = _load_max_file_size()

UPLOAD_ERROR_MESSAGES = {
    "invalid_extension": "Unsupported file type. Allowed types: .py, .js, .ts, .java, .cpp",
    "blocked_file": "Executable files are not allowed.",
    "invalid_mime": "Invalid MIME type detected.",
}
