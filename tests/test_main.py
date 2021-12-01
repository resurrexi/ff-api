import os

from fastapi.testclient import TestClient
from fastapi import status

from app import main

client = TestClient(main.app)


def test_get_main():
    """Should return 200 with welcome message."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Welcome, please refer to `/docs` for endpoints."
    }


def test_get_file_is_success_if_exists():
    """Should return 200 with file."""
    response = client.get("/file/docs/doc1.txt")
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b"test document 1\n"


def test_get_file_is_not_found_if_not_exists():
    """Should return 404."""
    response = client.get("/file/docs/does_not_exist.txt")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"message": "Path does not exist"}


def test_get_directory_is_success_if_exists():
    """Should return 200 with directory listing."""
    response = client.get("/file/docs")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "isDirectory": True,
        "files": [
            "newdoc.txt",
            "doc3.txt",
            "doc1.txt",
            "doc2.txt",
        ],
    }


def test_get_directory_is_not_found_if_not_exists():
    """Should return 404."""
    response = client.get("/file/nonexistent_dir")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"message": "Path does not exist"}


def test_get_directory_order_by_filename():
    """Should return 200 with directory listing."""
    response = client.get("/file/docs?orderBy=fileName")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "isDirectory": True,
        "files": [
            "newdoc.txt",
            "doc3.txt",
            "doc2.txt",
            "doc1.txt",
        ],
    }


def test_get_directory_order_by_size_ascending():
    """Should return 200 with directory listing."""
    response = client.get("/file/docs?orderBy=size&orderByDirection=Ascending")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "isDirectory": True,
        "files": [
            "doc2.txt",
            "doc3.txt",
            "doc1.txt",
            "newdoc.txt",
        ],
    }


def test_get_directory_filter_by_name():
    """Should return 200 with filtered file."""
    response = client.get("/file/docs?filterByName=new")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "isDirectory": True,
        "files": [
            "newdoc.txt",
        ],
    }


def test_get_directory_filter_by_name_nonexistent():
    """Should return 200 with empty file list."""
    response = client.get("/file/docs?filterByName=nonexistent")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"isDirectory": True, "files": []}
