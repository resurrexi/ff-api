import os
import tempfile
import shutil

import pytest

from app import main


@pytest.fixture(autouse=True)
def test_directory(monkeypatch):
    """Set up test directory."""
    # create temporary dir
    tmpdir = tempfile.mkdtemp()

    # copy fixtures to temp directory
    source = os.path.join(main.BASE_DIR, "tests", "fixtures")
    dest = os.path.join(tmpdir, "fixtures")
    shutil.copytree(source, dest)

    # patch the API_FILE_DIR setting
    monkeypatch.setattr(main, "API_FILE_DIR", dest)

    yield dest

    # teardown
    shutil.rmtree(tmpdir)
