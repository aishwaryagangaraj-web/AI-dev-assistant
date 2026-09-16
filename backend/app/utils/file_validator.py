import logging
from pathlib import Path

import magic

from .upload_config import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    BLOCKED_EXTENSIONS,
    UPLOAD_ERROR_MESSAGES,
)

logger = logging.getLogger(__name__)


def sanitize_and_check_filename(filename: str) -> str:
    """Ensures filename is a non-empty string without null bytes or unsafe formatting."""
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError(UPLOAD_ERROR_MESSAGES["invalid_extension"])

    if "\x00" in filename:
        raise ValueError(UPLOAD_ERROR_MESSAGES["blocked_file"])

    cleaned = Path(filename.strip().rstrip(".")).name
    if not cleaned:
        raise ValueError(UPLOAD_ERROR_MESSAGES["invalid_extension"])

    return cleaned


def get_file_extension(filename: str) -> str:
    clean_filename = sanitize_and_check_filename(filename)
    return Path(clean_filename).suffix.lower()


def has_double_extension(filename: str) -> bool:
    clean_filename = sanitize_and_check_filename(filename)
    suffixes = [suffix.lower() for suffix in Path(clean_filename).suffixes]

    if len(suffixes) <= 1:
        return False

    return any(ext in BLOCKED_EXTENSIONS for ext in suffixes[:-1])


def validate_file_extension(filename: str) -> str:
    clean_filename = sanitize_and_check_filename(filename)
    extension = get_file_extension(clean_filename)

    if not extension:
        raise ValueError(UPLOAD_ERROR_MESSAGES["invalid_extension"])

    if has_double_extension(clean_filename):
        raise ValueError(UPLOAD_ERROR_MESSAGES["blocked_file"])

    if extension in BLOCKED_EXTENSIONS:
        raise ValueError(UPLOAD_ERROR_MESSAGES["blocked_file"])

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(UPLOAD_ERROR_MESSAGES["invalid_extension"])

    return extension


def detect_mime_type(file_content: bytes) -> str:
    if not isinstance(file_content, bytes) or len(file_content) == 0:
        raise ValueError("File content cannot be empty.")

    try:
        mime = magic.Magic(mime=True)
        return mime.from_buffer(file_content)
    except Exception as err:
        logger.error("Error detecting MIME type: %s", err)
        raise ValueError("Unable to determine file MIME type.") from err


def validate_mime_type(ext: str, filecontent: bytes) -> str:
    detected_mime = detect_mime_type(filecontent)
    logger.debug("Detected MIME Type: %s", detected_mime)

    allowed_mimes = ALLOWED_MIME_TYPES.get(ext)
    if not allowed_mimes or detected_mime not in allowed_mimes:
        raise ValueError(
            f"{UPLOAD_ERROR_MESSAGES['invalid_mime']}"
            f"Detected MIME Type : {detected_mime}"
        )

    return detected_mime


def validate_file(filename: str, filecontent: bytes) -> str:
    ext = validate_file_extension(filename)
    mime_type = validate_mime_type(ext=ext, filecontent=filecontent)
    return mime_type