from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
import uvicorn
import os
import subprocess
import uuid

app = FastAPI()

@app.post("/process")
async def process_video(video_url: str = Form(...)):
    if not video_url or not video_url.strip():
        return {"error": "No video URL provided to process."}

    # Create unique filename
    filename = str(uuid.uuid4())
    input_path = f"/tmp/{filename}.mp4"
    output_path = f"/tmp/{filename}_branded.mp4"
    overlay_path = "overlay.png"

    # Step 1: Download video using yt-dlp
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

    # Step 2: Apply overlay using ffmpeg
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # overwrite if needed
        "-i", input_path,
        "-i", overlay_path,
        "-filter_complex", "overlay=0:0",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        output_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"FFmpeg failed: {e}"}

    # Step 3: Validate that video file actually exists and isn't empty
    if not os.path.exists(output_path) or os.path.getsize(output_path) < 500000:
        return {"error": "Output file is missing or too small — possible FFmpeg failure."}

    return FileResponse(path=output_path, filename="output.mp4", media_type="video/mp4")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
