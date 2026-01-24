import os
import uuid
import subprocess
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = FastAPI(title="Private Media Downloader")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/download")
async def download_video(
    request: Request,
    url: str = Form(...),
    platform: str = Form(...)
):
    file_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    ydl_cmd = [
        "yt-dlp",
        "-f", "bv*+ba/best",
        "--merge-output-format", "mp4",
        "-o", output_path,
        "--no-playlist",
        url
    ]

    subprocess.run(ydl_cmd, check=True)

    # Find downloaded file
    for file in os.listdir(DOWNLOAD_DIR):
        if file.startswith(file_id):
            return FileResponse(
                path=os.path.join(DOWNLOAD_DIR, file),
                filename=file,
                media_type="application/octet-stream"
            )

    return {"error": "Download failed"}
