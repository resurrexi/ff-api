import os
import aiofiles
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

# We should explicitly set a working path that the API can work on.
# This is for security reasons as allowing any path can run the risk
# of breaking FastAPI or the system. For example, if we allow
# operations on OS system paths, e.g. `/usr/bin`, we could break the
# OS, not to mention that these sensitive paths also require superuser
# privileges to be operated on.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_FILE_DIR = os.path.join(BASE_DIR, "files")

# Set chunksize for writing to files when uploading
CHUNKSIZE = 1024

app = FastAPI()


@app.get("/")
async def main():
    return {"message": "Welcome, please refer to `/docs` for endpoints."}


@app.get("/file/{localSystemFilePath:path}")
async def get_path(localSystemFilePath: str):
    abs_path = os.path.join(API_FILE_DIR, localSystemFilePath)

    if os.path.exists(abs_path):
        if os.path.isdir(abs_path):
            return {"isDirectory": True, "files": os.listdir(abs_path)}
        return FileResponse(abs_path)
    return JSONResponse(
        content={"message": "Path does not exist"},
        status_code=status.HTTP_404_NOT_FOUND
    )


@app.post("/file/{localSystemFilePath:path}")
async def upload_file(localSystemFilePath: str, file: UploadFile = File(...)):
    abs_path = os.path.join(API_FILE_DIR, localSystemFilePath)

    if os.path.exists(abs_path):
        return JSONResponse(
            content={"message": "File already exists"},
            status_code=status.HTTP_403_FORBIDDEN
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
        content={"message": f"File has been uploaded to {localSystemFilePath}"},
        status_code=status.HTTP_201_CREATED
    )


@app.patch("/file/{localSystemFilePath:path}")
async def update_file(localSystemFilePath: str, file: UploadFile = File(...)):
    abs_path = os.path.join(API_FILE_DIR, localSystemFilePath)

    if not os.path.exists(abs_path):
        return JSONResponse(
            content={"message": "File does not exist"},
            status_code=status.HTTP_404_NOT_FOUND
        )

    async with aiofiles.open(abs_path, "wb") as file_w:
        while True:
            chunk = await file.read(CHUNKSIZE)
            if not chunk:
                break
            await file_w.write(chunk)

    return JSONResponse(
        content={"message": f"{localSystemFilePath} has been updated"},
        status_code=status.HTTP_200_OK
    )


@app.delete("/file/{localSystemFilePath:path}")
async def delete_file(localSystemFilePath: str):
    abs_path = os.path.join(API_FILE_DIR, localSystemFilePath)

    try:
        os.remove(abs_path)
        return JSONResponse(
            content={"message": f"{localSystemFilePath} has been deleted"},
            status_code=status.HTTP_200_OK
        )
    except FileNotFoundError:
        return JSONResponse(
            content={"message": "File does not exist"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    except OSError:
        return JSONResponse(
            content={"message": "Not a file"},
            status_code=status.HTTP_403_FORBIDDEN
        )
