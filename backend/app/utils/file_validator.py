import logging
import time
from pathlib import Path

import magic

from .upload_config import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    BLOCKED_EXTENSIONS,
    UPLOAD_ERROR_MESSAGES,
)

logger = logging.getLogger(__name__)


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def has_double_extension(filename: str) -> bool:
    suffixes = Path(filename).suffixes

    if len(suffixes) <= 1:
        return False

    return any(ext in BLOCKED_EXTENSIONS for ext in suffixes[:-1])


def validate_file_extension(filename: str) -> str:
    extension = get_file_extension(filename)

    if not extension:
        logger.warning("Validation failed: missing extension for filename='%s'", filename)
        raise ValueError(UPLOAD_ERROR_MESSAGES["invalid_extension"])

    if has_double_extension(filename):
        logger.warning("Validation failed: double extension detected in filename='%s'", filename)
        raise ValueError(UPLOAD_ERROR_MESSAGES["blocked_file"])

    if extension in BLOCKED_EXTENSIONS:
        logger.warning("Validation failed: blocked extension '%s' in filename='%s'", extension, filename)
        raise ValueError(UPLOAD_ERROR_MESSAGES["blocked_file"])

    if extension not in ALLOWED_EXTENSIONS:
        logger.warning("Validation failed: unsupported extension '%s' for filename='%s'", extension, filename)
        raise ValueError(UPLOAD_ERROR_MESSAGES["invalid_extension"])

    logger.debug("Extension validation passed for '%s': %s", filename, extension)
    return extension


def detect_mime_type(file_content: bytes) -> str:
    mime = magic.Magic(mime=True)
    return mime.from_buffer(file_content)


def validate_mime_type(ext: str, filecontent: bytes) -> str:
    detected_mime = detect_mime_type(filecontent)
    logger.debug("Detected MIME type: %s for extension: %s", detected_mime, ext)

    if detected_mime not in ALLOWED_MIME_TYPES.get(ext, []):
        logger.warning(
            "Validation failed: MIME type mismatch for ext='%s'. Detected='%s'",
            ext,
            detected_mime,
        )
        raise ValueError(
            f"{UPLOAD_ERROR_MESSAGES['invalid_mime']}"
            f"Detected MIME Type : {detected_mime}"
        )

    return detected_mime


def validate_file(filename: str, filecontent: bytes) -> str:
    start_time = time.perf_counter()
    file_size = len(filecontent)

    logger.info(
        "Starting file validation for '%s' (size=%d bytes)",
        filename,
        file_size,
        extra={
            "event": "file_validation_start",
            "file_name": filename,
            "file_size_bytes": file_size,
        },
    )

    try:
        ext = validate_file_extension(filename)
        mime_type = validate_mime_type(ext=ext, filecontent=filecontent)

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "File validation successful for '%s' (MIME: %s) in %.2f ms",
            filename,
            mime_type,
            duration_ms,
            extra={
                "event": "file_validation_success",
                "file_name": filename,
                "extension": ext,
                "mime_type": mime_type,
                "file_size_bytes": file_size,
                "duration_ms": round(duration_ms, 2),
            },
        )
        return mime_type

    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.error(
            "File validation failed for '%s' after %.2f ms: %s",
            filename,
            duration_ms,
            str(exc),
            extra={
                "event": "file_validation_failure",
                "file_name": filename,
                "file_size_bytes": file_size,
                "error": str(exc),
                "duration_ms": round(duration_ms, 2),
            },
            exc_info=True,
        )
        raise