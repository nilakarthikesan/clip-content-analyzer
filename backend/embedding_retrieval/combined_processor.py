import os
import requests
from moviepy import VideoFileClip
from typing import List
import numpy as np
from PIL import Image
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://bbrvvbipmfdiyekyilbo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJicnZ2YmlwbWZkaXlla3lpbGJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIwMzc5MzMsImV4cCI6MjA2NzYxMzkzM30.FBzWwcIrorGSHg49CV-nmEyNxZHnewwwL5QMu3Gofrs"

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_media_clips():
    supabase = get_supabase_client()
    response = supabase.table('media_clips').select('*').execute()
    return response.data

def extract_frames_at_percentages(video_path: str, percentages: List[float] = [0.25, 0.5, 0.75]) -> List[Image.Image]:
    """
    Extract frames from the video at the given percentages of its duration.
    Returns a list of PIL Images.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    clip = VideoFileClip(video_path)
    duration = clip.duration
    frames = []
    for pct in percentages:
        t = duration * pct
        frame = clip.get_frame(t)
        # Convert numpy array to PIL Image
        img = Image.fromarray(np.uint8(frame))
        frames.append(img)
    clip.close()
    return frames

def download_video(url, local_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def process_all_clips():
    clips = fetch_media_clips()
    print(f"Found {len(clips)} clips in database")
    
    for clip in clips:
        video_url = clip['clip_path']
        local_path = f"/tmp/{clip['id']}.mov"
        try:
            print(f"Processing: {clip['title']}")
            print(f"Downloading {video_url} ...")
            download_video(video_url, local_path)
            frames = extract_frames_at_percentages(local_path)
            for i, img in enumerate(frames):
                img.save(f"{clip['id']}_frame_{i+1}.jpg")
            print(f"✓ Extracted 3 frames for {clip['title']}")
        except Exception as e:
            print(f"✗ Failed to process {clip['title']}: {e}")
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

if __name__ == "__main__":
    process_all_clips() 