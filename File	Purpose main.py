from fastapi import FastAPI, Request
import subprocess
import uuid
import os
import uvicorn

app = FastAPI()

@app.post("/process")
async def process_video(request: Request):
    data = await request.json()
    video_url = data.get("url")

    if not video_url:
        return {"error": "Missing video URL"}

    filename = f"{uuid.uuid4()}.mp4"
    output_path = f"/app/processed/{filename}"
    raw_path = f"/app/raw/raw_{filename}"

    os.makedirs("/app/raw", exist_ok=True)
    os.makedirs("/app/processed", exist_ok=True)

    try:
        # Step 1: Download raw video
        subprocess.run([
            "yt-dlp", "-f", "mp4", "-o", raw_path, video_url
        ], check=True)

        # Step 2: Apply overlay
        overlay_path = "/app/overlay.png"
        subprocess.run([
            "ffmpeg", "-y", "-i", raw_path, "-i", overlay_path,
            "-filter_complex", "overlay=W-w-20:H-h-20",
            "-preset", "fast", output_path
        ], check=True)

        return {
            "message": "Success",
            "video_url": f"{request.base_url}videos/{filename}"
        }

    except subprocess.CalledProcessError as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
