import os
import uuid
import subprocess
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Media Downloader")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/download")
async def download_video(url: str = Form(...)):
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
        print("❌ yt-dlp error:", result.stderr)
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Download failed. YouTube and Facebook may have limitations on cloud hosting."
            }
        )

    for file in os.listdir(DOWNLOAD_DIR):
        if file.startswith(file_id):
            file_path = os.path.join(DOWNLOAD_DIR, file)
            print("✅ Sending file:", file)

            return FileResponse(
                path=file_path,
                filename=file,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f'attachment; filename="{file}"'
                }
            )

    return JSONResponse(
        status_code=404,
        content={"status": "error", "message": "File not found"}
    )
