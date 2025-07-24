# main.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from utils import upload_file, list_files, download_file, delete_file, get_storage_usage
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_STORAGE_MB = 150

@app.get("/")
def root():
    return {"message": "Cloud Storage Microservice Running 🚀 Lesgoo"}

@app.post("/upload/")
async def upload(user_id: str = Form(...), file: UploadFile = File(...), path: str = Form("")):
    size_limit = MAX_STORAGE_MB * 1024 * 1024
    current_usage = get_storage_usage(user_id)

    contents = await file.read()
    file_size = len(contents)

    if current_usage + file_size > size_limit:
        return JSONResponse(status_code=400, content={"error": "Storage quota exceeded"})

    # Reset file pointer for S3 to read the file
    from io import BytesIO
    file.file = BytesIO(contents)

    relative_path = file.filename if not path else path

    result = upload_file(file.file, relative_path, user_id)

    return result



@app.get("/files/{user_id}")
def list_user_files(user_id: str):
    return list_files(user_id)

@app.get("/download/")
def get_download_url(user_id: str, filename: str):
    return {"url": download_file(filename, user_id)}

@app.delete("/delete/")
def delete_user_file(user_id: str, filename: str):
    return delete_file(filename, user_id)

@app.get("/quota/{user_id}")
def check_quota(user_id: str):
    used = get_storage_usage(user_id)
    percent = round((used / (MAX_STORAGE_MB * 1024 * 1024)) * 100, 2)
    alert = percent >= 75
    return {
        "used_MB": round(used / (1024 * 1024), 2),
        "max_MB": MAX_STORAGE_MB,
        "usage_percent": percent,
        "alert": alert
    }