import os

import pytest

from app import main


@pytest.fixture(autouse=True)
def set_fixture_directory(monkeypatch):
    """Patch the API_FILE_DIR setting."""
    monkeypatch.setattr(
        main, "API_FILE_DIR", os.path.join(main.BASE_DIR, "tests", "fixtures")
    )
