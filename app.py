import os
import subprocess
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/')
def process_video():
    url = request.args.get('url')
    if not url:
        return 'Missing URL', 400

    try:
        # Step 1: Download with yt-dlp
        subprocess.run(['yt-dlp', '-o', 'input.mp4', url], check=True)

        # Step 2: Overlay with ffmpeg
        subprocess.run([
            'ffmpeg', '-i', 'input.mp4', '-i', 'overlay.png',
            '-filter_complex', 'overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2',
            '-preset', 'veryfast', '-y', 'output.mp4'
        ], check=True)

        return send_file('output.mp4', mimetype='video/mp4')

    except subprocess.CalledProcessError as e:
        return f'Error processing video: {e}', 500

