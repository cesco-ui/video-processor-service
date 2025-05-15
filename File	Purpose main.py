from fastapi import FastAPI, UploadFile, File
import subprocess

app = FastAPI()

@app.post("/process")
async def process_video(file: UploadFile = File(...)):
    with open("input.mp4", "wb") as f:
        f.write(await file.read())

    # Run ffmpeg to apply the overlay
    cmd = [
        "ffmpeg",
        "-i", "input.mp4",
        "-i", "overlay.png",
        "-filter_complex", "[0:v][1:v] overlay=0:0",
        "-c:a", "copy",
        "output.mp4"
    ]
    subprocess.run(cmd, check=True)

    return {"message": "Video processed", "output_file": "output.mp4"}
