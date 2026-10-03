import logging
from pathlib import Path

import magic

from .upload_config import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    BLOCKED_EXTENSIONS,
    UPLOAD_ERROR_MESSAGES,
)

# REFACTOR 1: Move logger to the module level for efficiency
logger = logging.getLogger(__name__)


def get_file_extension(filename: str) -> str:
    """Extracts the lowercased file extension."""
    return Path(filename).suffix.lower()


def has_double_extension(filename: str) -> bool:
    """Checks for malicious double extensions (e.g., script.exe.txt)."""
    suffixes = Path(filename).suffixes

    if len(suffixes) <= 1:
        return False

    return any(ext in BLOCKED_EXTENSIONS for ext in suffixes[:-1])


# REFACTOR 2: Fix type hint (returns str, not None)
def validate_file_extension(filename: str) -> str:
    extension = get_file_extension(filename)

    if not extension:
        raise ValueError(UPLOAD_ERROR_MESSAGES["invalid_extension"])

    # REFACTOR 3: Combine identical error branches
    if has_double_extension(filename) or extension in BLOCKED_EXTENSIONS:
        raise ValueError(UPLOAD_ERROR_MESSAGES["blocked_file"])

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(UPLOAD_ERROR_MESSAGES["invalid_extension"])
        
    return extension


def detect_mime_type(file_content: bytes) -> str:
    mime = magic.Magic(mime=True)
    return mime.from_buffer(file_content)


# REFACTOR 2: Fix type hint (returns str, not None)
def validate_mime_type(ext: str, filecontent: bytes) -> str:
    detected_mime = detect_mime_type(filecontent)
    logger.debug("Detected MIME Type: %s for extension: %s", detected_mime, ext)
    
    # REFACTOR 4: Safe dictionary access to prevent KeyError crashes
    allowed_mimes = ALLOWED_MIME_TYPES.get(ext, [])
    
    if detected_mime not in allowed_mimes:
        raise ValueError(
            f"{UPLOAD_ERROR_MESSAGES['invalid_mime']} "
            f"Detected MIME Type: {detected_mime}"
        )
    return detected_mime


# REFACTOR 2: Fix type hint (returns str, not None)
def validate_file(filename: str, filecontent: bytes) -> str:
    """
    Validates both the extension and MIME type of an uploaded file.
    Returns the detected MIME type if successful.
    """
    ext = validate_file_extension(filename)
    mime_type = validate_mime_type(ext, filecontent)

    return mime_type