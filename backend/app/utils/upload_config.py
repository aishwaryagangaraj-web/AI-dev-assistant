import os
from typing import Dict, Any, List, Set

ALLOWED_EXTENSIONS: List[str] = [".py", ".js", ".ts", ".java", ".cpp", ".txt"]

ALLOWED_MIME_TYPES: Dict[str, List[str]] = {
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

BLOCKED_EXTENSIONS: List[str] = [
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

max_file_size = 5 * 1024 * 1024  # 5 MB

UPLOAD_ERROR_MESSAGES: Dict[str, str] = {
    "invalid_extension": (
        "Unsupported file type. " "Allowed types: .py, .js, .ts, .java, .cpp"
    ),
    "blocked_file": "Executable files are not allowed.",
    "invalid_mime": "Invalid MIME type detected.",
}


class UploadConfigError(ValueError):
    """Custom exception raised when upload configuration validation fails."""
    pass


def validate_upload_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Hardens and validates upload configuration payload inputs."""
    if not isinstance(config, dict):
        raise UploadConfigError("Configuration payload must be a non-null dictionary.")

    validated: Dict[str, Any] = {}

    # 1. Validate max_file_size
    size = config.get("max_file_size", max_file_size)
    if not isinstance(size, int) or isinstance(size, bool):
        raise UploadConfigError("max_file_size must be a valid integer.")
    if size <= 0:
        raise UploadConfigError("max_file_size must be a positive integer greater than zero.")
    if size > 50 * 1024 * 1024:  # Upper bound safety check: 50MB
        raise UploadConfigError("max_file_size exceeds maximum allowed limit of 50MB.")
    validated["max_file_size"] = size

    # 2. Validate allowed_extensions
    raw_exts = config.get("allowed_extensions", ALLOWED_EXTENSIONS)
    if isinstance(raw_exts, (list, set, tuple)):
        if len(raw_exts) == 0:
            raise UploadConfigError(UPLOAD_ERROR_MESSAGES["invalid_extension"])

        cleaned_exts: List[str] = []
        for ext in raw_exts:
            if not isinstance(ext, str) or not ext.strip():
                raise UploadConfigError("Each extension in allowed_extensions must be a non-empty string.")
            
            ext_str = ext.strip().lower()
            if not ext_str.startswith("."):
                ext_str = f".{ext_str}"

            if ext_str in BLOCKED_EXTENSIONS:
                raise UploadConfigError(UPLOAD_ERROR_MESSAGES["blocked_file"])

            if ext_str not in cleaned_exts:
                cleaned_exts.append(ext_str)

        validated["allowed_extensions"] = cleaned_exts
    else:
        raise UploadConfigError("allowed_extensions must be a list or set of string extensions.")

    # 3. Validate MIME types mapping
    mime_types = config.get("allowed_mime_types", ALLOWED_MIME_TYPES)
    if isinstance(mime_types, dict):
        validated["allowed_mime_types"] = mime_types
    else:
        raise UploadConfigError(UPLOAD_ERROR_MESSAGES["invalid_mime"])

    return validated