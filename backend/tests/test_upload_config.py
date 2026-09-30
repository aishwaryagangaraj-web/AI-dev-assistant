import pytest
from app.utils.upload_config import _load_max_file_size

def test_load_max_file_size_valid(monkeypatch):
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "10")
    assert _load_max_file_size() == 10 * 1024 * 1024

def test_load_max_file_size_default(monkeypatch):
    monkeypatch.delenv("MAX_FILE_SIZE_MB", raising=False)
    assert _load_max_file_size() == 5 * 1024 * 1024

def test_load_max_file_size_invalid_type(monkeypatch):
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "not_a_number")
    with pytest.raises(ValueError, match="Invalid upload configuration"):
        _load_max_file_size()

def test_load_max_file_size_negative(monkeypatch):
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "-1")
    with pytest.raises(ValueError, match="MAX_FILE_SIZE_MB must be positive"):
        _load_max_file_size()
