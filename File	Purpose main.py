from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import subprocess
import os

app = FastAPI()

@app.post("/process")
async def process_video(file: UploadFile = File(...)):
    input_path = "input.mp4"
    output_path = "output.mp4"
    overlay_path = "overlay.png"

    # Save uploaded file
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())

    # Run FFmpeg command to apply the overlay
    command = [
        "ffmpeg",
        "-i", input_path,
        "-i", overlay_path,
        "-filter_complex", "[0:v][1:v] overlay=0:0",
        "-c:a", "copy",
        output_path
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"FFmpeg failed: {str(e)}"}

    # Return the processed video file
    return FileResponse(output_path, media_type="video/mp4", filename="output.mp4")
