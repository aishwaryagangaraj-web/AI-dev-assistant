import logging
from unittest.mock import patch
from app.utils.file_validator import validate_file


def test_validate_file_observability_logging(caplog):
    with patch("app.utils.file_validator.validate_file_extension", return_value=".pdf"), \
         patch("app.utils.file_validator.validate_mime_type", return_value="application/pdf"):
        
        with caplog.at_level(logging.INFO):
            mime = validate_file("sample.pdf", b"dummy pdf content")

        assert mime == "application/pdf"
        assert "Starting file validation for 'sample.pdf'" in caplog.text
        assert "File validation successful for 'sample.pdf'" in caplog.text