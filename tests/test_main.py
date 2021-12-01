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


def test_upload_file_is_success_if_path_is_new(test_directory):
    """Should return 201."""
    response = client.post(
        "/file/docs/uploaded.txt",
        files={"file": ("filename", b"uploaded file")},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert "File has been uploaded" in response.json()["message"]

    # ensure uploaded file is in the target directory
    assert "uploaded.txt" in os.listdir(os.path.join(test_directory, "docs"))


def test_upload_file_is_forbidden_if_path_exists():
    """Should return 403."""
    response = client.post(
        "/file/docs/doc1.txt",
        files={"file": ("filename", b"uploaded file")},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"message": "File already exists"}


def test_update_file_is_success_if_file_exists(test_directory):
    """Should return 200."""
    response = client.patch(
        "/file/docs/doc1.txt",
        files={"file": ("filename", b"uploaded file")},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "has been updated" in response.json()["message"]

    # ensure updated file has new contents
    with open(
        os.path.join(test_directory, "docs", "doc1.txt"), "rb"
    ) as file_r:
        assert b"uploaded file" in file_r.read()


def test_update_file_is_not_found_if_file_not_exists():
    """Should return 404."""
    response = client.patch(
        "/file/docs/does_not_exist.txt",
        files={"file": ("filename", b"uploaded file")},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"message": "File does not exist"}


def test_delete_file_success_if_is_file_and_exists(test_directory):
    """Should return 200."""
    response = client.delete("/file/docs/newdoc.txt")
    assert response.status_code == status.HTTP_200_OK
    assert "has been deleted" in response.json()["message"]

    # ensure file no longer exists in target directory
    assert "newdoc.txt" not in os.listdir(os.path.join(test_directory, "docs"))


def test_delete_file_is_not_found_if_file_not_exists():
    """Should return 404."""
    response = client.delete("/file/docs/does_not_exist.txt")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"message": "File does not exist"}


def test_delete_file_is_forbidden_if_path_is_directory():
    """Should return 403."""
    response = client.delete("/file/docs")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"message": "Not a file"}
