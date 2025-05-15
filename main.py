from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
import uvicorn
import os
import subprocess
import uuid

app = FastAPI()

@app.post("/process")
async def process_video(video_url: str = Form(...)):
    # Create unique filename for each request
    filename = str(uuid.uuid4())
    input_path = f"/tmp/{filename}.mp4"
    output_path = f"/tmp/{filename}_branded.mp4"

    # Download video using yt-dlp
    download_cmd = [
        "yt-dlp",
        "-f", "mp4",
        "-o", input_path,
        video_url
    ]

    try:
        subprocess.run(download_cmd, check=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to download video: {e}"}

    # Apply overlay using ffmpeg
    overlay_path = "overlay.png"
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_path,
        "-i", overlay_path,
        "-filter_complex", "overlay=0:0",
        "-c:a", "copy",
        output_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"FFmpeg failed: {e}"}

    return FileResponse(path=output_path, filename="output.mp4", media_type="video/mp4")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
