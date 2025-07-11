import os
import requests
from frame_extractor import extract_frames_at_percentages
from supabase_client import fetch_media_clips

# Downloads a video from a url 
# saves it as a local file because imoviepy has trouble processing urls that are not local files 
def download_video(url, local_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

# Goes through every video in the databse 
# downloads videos with the download video function and 
# extract three frames with the extractor function 
def process_all_clips():
    clips = fetch_media_clips()
    for clip in clips:
        # storing the clip path a video url variable 
        video_url = clip['clip_path']
        # storing the clip id as a path variable 
        local_path = f"/tmp/{clip['id']}.mov"
        try:
            print(f"Downloading {video_url} ...")
            download_video(video_url, local_path)
            # stores the three frames 
            frames = extract_frames_at_percentages(local_path)
            for i, img in enumerate(frames):
                img.save(f"{clip['id']}_frame_{i+1}.jpg")
            print(f"Extracted frames for {video_url}")
        except Exception as e:
            print(f"Failed to process {video_url}: {e}")
        finally:
            if os.path.exists(local_path):
                # removing the temp file to save space 
                os.remove(local_path)

if __name__ == "__main__":
    process_all_clips() 