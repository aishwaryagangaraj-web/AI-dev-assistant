import logging
import time

from fastapi import APIRouter, HTTPException, UploadFile, status

from ..utils.file_validator import validate_file
from ..utils.upload_config import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    BLOCKED_EXTENSIONS,
    max_file_size,
)

router = APIRouter(tags=["Upload Files"])
logger = logging.getLogger(__name__)


@router.get("/")
def index_upload():
    logger.info("Upload metadata endpoint accessed")
    return {
        "max_file_size_MB": f"{ max_file_size / (1024 * 1024):.2f} MB",
        "blocked_extensions": BLOCKED_EXTENSIONS,
        "allowed_extensions": ALLOWED_EXTENSIONS,
        "allowed_mime_types": ALLOWED_MIME_TYPES,
    }


@router.post("/validate")
async def upload_file(file: UploadFile):
    start_time = time.perf_counter()

    if file is None or not getattr(file, "filename", None):
        logger.warning("Upload attempt failed: Missing file payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded"
        )

    filename = file.filename
    filecontent = await file.read()
    filesize = len(filecontent)

    logger.info(
        "Upload validation started: filename='%s', bytes=%d",
        filename,
        filesize,
    )

    # Validate max size
    if filesize > max_file_size:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.warning(
            "Upload rejected: File size limit exceeded | filename='%s', bytes=%d, max_bytes=%d, duration_ms=%.2f",
            filename,
            filesize,
            max_file_size,
            duration_ms,
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size should not exceed {max_file_size / (1024 * 1024)} MB",
        )
    try:
        detected_mime = validate_file(filename=filename, filecontent=filecontent)
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "Upload validation successful: filename='%s', mime='%s', bytes=%d, duration_ms=%.2f",
            filename,
            detected_mime,
            filesize,
            duration_ms,
        )

        return {
            "success": True,
            "filename": filename,
            "content_type": detected_mime,
            "size": f"{filesize/1024:.2f} KB",
        }

    except ValueError as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.error(
            "Upload validation failed: filename='%s', error='%s', duration_ms=%.2f",
            filename,
            str(e),
            duration_ms,
        )
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e)
        )