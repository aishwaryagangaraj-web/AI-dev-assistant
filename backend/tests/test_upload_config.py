import pytest
from app.utils.upload_config import validate_upload_config, UploadConfigError, UPLOAD_ERROR_MESSAGES

def test_valid_upload_config():
    config = {
        "max_file_size": 5242880,
        "allowed_extensions": [".py", ".js"],
    }
    result = validate_upload_config(config)
    assert result["max_file_size"] == 5242880
    assert result["allowed_extensions"] == [".py", ".js"]

def test_blocked_extension_rejection():
    with pytest.raises(UploadConfigError, match=UPLOAD_ERROR_MESSAGES["blocked_file"]):
        validate_upload_config({"allowed_extensions": [".exe", ".py"]})

def test_invalid_max_file_size_type():
    with pytest.raises(UploadConfigError, match="must be a valid integer"):
        validate_upload_config({"max_file_size": "5MB"})

def test_negative_max_file_size():
    with pytest.raises(UploadConfigError, match="positive integer"):
        validate_upload_config({"max_file_size": -100})