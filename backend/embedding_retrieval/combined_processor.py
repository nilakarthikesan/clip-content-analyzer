import os
import requests
# from moviepy import VideoFileClip
# from typing import List
# import numpy as np
# from PIL import Image
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

# def extract_frames_at_percentages(video_path: str, percentages: List[float] = [0.25, 0.5, 0.75]) -> List[Image.Image]:
#     """
#     Extract frames from the video at the given percentages of its duration.
#     Returns a list of PIL Images.
#     """
#     if not os.path.exists(video_path):
#         raise FileNotFoundError(f"Video file not found: {video_path}")
#     clip = VideoFileClip(video_path)
#     duration = clip.duration
#     frames = []
#     for pct in percentages:
#         t = duration * pct
#         frame = clip.get_frame(t)
#         # Convert numpy array to PIL Image
#         img = Image.fromarray(np.uint8(frame))
#         frames.append(img)
#     clip.close()
#     return frames


# downloads a video from a url and saves it as a local file 
def download_video(url, local_path):
    print(f"  Starting download from: {url}")
    print(f"  Saving to: {local_path}")
    
    try:
        # sending an http request to download a file from a url 
        # url is where the video is stored 
        # we want to download the video in chunks not all at once 
        print(f"  Making HTTP request...")
        response = requests.get(url, stream=True)
        print(f"  HTTP response status: {response.status_code}")
        
        print(f"  Checking for errors...")
        response.raise_for_status()
        print(f"  No HTTP errors found")
        
        print(f"  Opening file for writing...")
        with open(local_path, 'wb') as f:
            print(f"  Starting to write chunks...")
            chunk_count = 0
            # loop goes through each piece of the video and writes each piece to a local file on my computer 
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                chunk_count += 1
                if chunk_count % 100 == 0:  # Print progress every 100 chunks
                    print(f"    Written {chunk_count} chunks...")
            
            print(f"  Download completed! Total chunks: {chunk_count}")
            
    except requests.exceptions.RequestException as e:
        print(f"  ✗ HTTP/Network error: {e}")
        raise
    except IOError as e:
        print(f"  ✗ File writing error: {e}")
        raise
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        raise 


def process_all_clips():
    # store all the clips in the database 
    clips = fetch_media_clips()
    print(f"Found {len(clips)} clips in database")
    
    for clip in clips:
        # storing the video urls we find in the database here 
        video_url = clip['clip_path']
        print(f"\n=== CLIP INFO ===")
        print(f"Title: {clip['title']}")
        print(f"Clip path from DB: '{video_url}'")
        print(f"URL type: {type(video_url)}")
        # creating a temp local path to store the video 
        local_path = f"/tmp/{clip['id']}.mov"
        try:
            print(f"Processing: {clip['title']}")
            print(f"Downloading {video_url} ...")

            download_video(video_url, local_path)
            print(f"✓ Download completed for {clip['title']}")
            
            # Check if file was actually downloaded
            if os.path.exists(local_path):
                print(f"✓ File confirmed at: {local_path}")
            else:
                print(f"✗ File not found at: {local_path}")

        #     frames = extract_frames_at_percentages(local_path)
        #     for i, img in enumerate(frames):
        #         img.save(f"{clip['id']}_frame_{i+1}.jpg")
        #     print(f"✓ Extracted 3 frames for {clip['title']}")
        except Exception as e:
            #print(f"✗ Failed to process {clip['title']}: {e}")
            print("failed to download video", )
        # finally:
        #     if os.path.exists(local_path):
        #         os.remove(local_path)

if __name__ == "__main__":
    process_all_clips() 
    # clips = fetch_media_clips()
    # print(clips) 
