import os
import uuid
import subprocess
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Private Media Downloader")
app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/download")
async def download_video(
    request: Request,
    url: str = Form(...)
):
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    command = [
        "yt-dlp",
        "-f", "bv*+ba/best",
        "--merge-output-format", "mp4",
        "--no-playlist",
        "-o", output_template,
        url
    ]

    result = subprocess.run(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
    if result.returncode != 0:
        return {
        "status": "error",
        "message": "Download failed. YouTube and Facebook may have limitations on cloud hosting."
    }


    for file in os.listdir(DOWNLOAD_DIR):
        if file.startswith(file_id):
            return FileResponse(
                path=os.path.join(DOWNLOAD_DIR, file),
                filename=file
            )

    return {"error": "Download failed"}
