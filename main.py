import os
from pathlib import Path
from typing import Optional
from enum import Enum

import aiofiles
from fastapi import FastAPI, File, UploadFile, Query, status
from fastapi.responses import FileResponse, JSONResponse

# Set a working path that the API can work on. This is for security
# reasons as allowing any path can run the risk of breaking FastAPI
# or the system.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_FILE_DIR = os.path.join(BASE_DIR, "files")
# Set chunksize for writing to files when uploading
CHUNKSIZE = 1024

app = FastAPI()


class OrderByEnum(str, Enum):
    """OrderBy enumerator."""

    LAST_MOD = "lastModified"
    SIZE = "size"
    FILENAME = "fileName"


class OrderByDirection(str, Enum):
    """OrderByDirection enumerator."""

    DSC = "Descending"
    ASC = "Ascending"


@app.get("/")
async def main():
    """Main API page."""
    return {"message": "Welcome, please refer to `/docs` for endpoints."}


@app.get("/file/{local_path:path}")
async def get_path(
    local_path: str,
    order_by: Optional[OrderByEnum] = Query(None, alias="orderBy"),
    order_direction: Optional[OrderByDirection] = Query(
        None, alias="orderByDirection"
    ),
    filter_name: Optional[str] = Query(None, alias="filterByName"),
):
    """Retrieve target path."""
    abs_path = os.path.join(API_FILE_DIR, local_path)

    if os.path.exists(abs_path):
        if os.path.isdir(abs_path):
            # generate listing with file metadata
            listing = []
            for file in os.listdir(abs_path):
                modified = os.path.getmtime(os.path.join(abs_path, file))
                size = os.path.getsize(os.path.join(abs_path, file))
                listing.append((modified, size, file))

            # apply filtering
            if filter_name:
                listing = [
                    f for f in listing if filter_name.lower() in f[2].lower()
                ]

            # apply ordering
            if len(listing) > 1:
                reverse = order_direction == OrderByDirection.DSC
                if order_by == OrderByEnum.LAST_MOD:
                    listing.sort(key=lambda x: x[0], reverse=reverse)
                elif order_by == OrderByEnum.SIZE:
                    listing.sort(key=lambda x: x[1], reverse=reverse)
                else:
                    listing.sort(key=lambda x: x[2], reverse=reverse)

            # extract filenames from listing
            files = [f[2] for f in listing]

            return {"isDirectory": True, "files": files}
        return FileResponse(abs_path)
    return JSONResponse(
        content={"message": "Path does not exist"},
        status_code=status.HTTP_404_NOT_FOUND,
    )


@app.post("/file/{local_path:path}")
async def upload_file(local_path: str, file: UploadFile = File(...)):
    """Upload file to target path."""
    abs_path = os.path.join(API_FILE_DIR, local_path)

    if os.path.exists(abs_path):
        return JSONResponse(
            content={"message": "File already exists"},
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # ensure destination directory exists, otherwise create it
    destination = os.path.dirname(abs_path)
    if not os.path.exists(destination):
        # effective way to create nested directories if necessary
        Path(destination).mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(abs_path, "wb") as file_w:
        while True:
            chunk = await file.read(CHUNKSIZE)
            if not chunk:
                break
            await file_w.write(chunk)

    return JSONResponse(
        content={"message": f"File has been uploaded to {local_path}"},
        status_code=status.HTTP_201_CREATED,
    )


@app.patch("/file/{local_path:path}")
async def update_file(local_path: str, file: UploadFile = File(...)):
    """Update file at target path with uploaded file."""
    abs_path = os.path.join(API_FILE_DIR, local_path)

    if not os.path.exists(abs_path):
        return JSONResponse(
            content={"message": "File does not exist"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    async with aiofiles.open(abs_path, "wb") as file_w:
        while True:
            chunk = await file.read(CHUNKSIZE)
            if not chunk:
                break
            await file_w.write(chunk)

    return JSONResponse(
        content={"message": f"{local_path} has been updated"},
        status_code=status.HTTP_200_OK,
    )


@app.delete("/file/{local_path:path}")
async def delete_file(local_path: str):
    """Delete file at target path."""
    abs_path = os.path.join(API_FILE_DIR, local_path)

    try:
        os.remove(abs_path)
        return JSONResponse(
            content={"message": f"{local_path} has been deleted"},
            status_code=status.HTTP_200_OK,
        )
    except FileNotFoundError:
        return JSONResponse(
            content={"message": "File does not exist"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except OSError:
        return JSONResponse(
            content={"message": "Not a file"},
            status_code=status.HTTP_403_FORBIDDEN,
        )
