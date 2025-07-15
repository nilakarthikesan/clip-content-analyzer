import os
import requests
from moviepy import VideoFileClip
from typing import List
import numpy as np
from PIL import Image
from supabase import create_client, Client
from dotenv import load_dotenv
import torch
from transformers.models.clip.processing_clip import CLIPProcessor
from transformers.models.clip.modeling_clip import CLIPModel

load_dotenv()  # Loads variables from .env into environment

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and/or SUPABASE_KEY are not set. Check your .env file and environment variables.")

# Load CLIP model globally
print("Loading CLIP model...")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
print("✓ CLIP model loaded successfully")

def get_supabase_client() -> Client:
    # Type assertion to tell the linter these are strings (we already checked they're not None)
    return create_client(SUPABASE_URL, SUPABASE_KEY)  # type: ignore

def fetch_media_clips():
    supabase = get_supabase_client()
    response = supabase.table('media_clips').select('*').execute()
    return response.data

def get_image_embedding(image: Image.Image) -> np.ndarray:
    """
    Get CLIP embedding for a single image.
    Returns a numpy array of the embedding vector.
    """
    # Process the image through CLIP processor
    inputs = clip_processor(images=image, return_tensors="pt", padding=True)  # type: ignore
    
    # Get image features from CLIP model
    with torch.no_grad():
        image_features = clip_model.get_image_features(**inputs)  # type: ignore
    
    # Convert to numpy array and flatten
    return image_features.numpy().flatten()

def extract_frames_at_percentages(video_path: str, percentages: List[float] = [0.25, 0.5, 0.75]) -> List[Image.Image]:
    """
    Extract frames from the video at the given percentages of its duration.
    Returns a list of PIL Images.
    """

    # checks if the video path exists in the local file system 
    # if it doesnt then raise an error 
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # create a video clip object from the path 
    clip = VideoFileClip(video_path)
    duration = clip.duration
    frames = []
    for pct in percentages:
        t = duration * pct
        frame = clip.get_frame(t)
        # Convert numpy array to PIL Image
        if frame is None: 
            print(f"No frame found at {t} seconds for {video_path}")
            continue
        else: 
            print(f"Extracted frame at {t:.2f} seconds, shape: {getattr(frame, 'shape', None)}")
        img = Image.fromarray(np.uint8(frame))
        frames.append(img)
    clip.close()
    return frames


# downloads a video from a url and saves it as a local file 
def download_video(url, local_path):
    print(f"  Downloading from: {url}")
    print(f"  Saving to: {local_path}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  Download completed!")
    except Exception as e:
        print(f"  ✗ Download error: {e}")
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
        # Get the file extension from the URL
        file_extension = video_url.split('.')[-1].split('?')[0]  # Remove query parameters
        # creating a temp local path to store the video with correct extension
        local_path = f"/tmp/{clip['id']}.{file_extension}"
        try:
            print(f"Processing: {clip['title']}")
            download_video(video_url, local_path)
            print(f"✓ Download completed for {clip['title']}")
            
            # Check if file was actually downloaded
            if os.path.exists(local_path):
                print(f"✓ File confirmed at: {local_path}")
                
                # Extract frames from the downloaded video
                print(f"Extracting frames from {clip['title']}...")
                try:
                    frames = extract_frames_at_percentages(local_path)
                    print(f"✓ Extracted {len(frames)} frames for {clip['title']}")
                    
                    # Get embeddings for each frame
                    print(f"Getting embeddings for {clip['title']}...")
                    embeddings = []
                    for i, img in enumerate(frames):
                        # Save the frame
                        img.save(f"{clip['id']}_frame_{i+1}.jpg")
                        
                        # Get embedding for this frame
                        embedding = get_image_embedding(img)
                        embeddings.append(embedding)
                        print(f"  Frame {i+1} embedding: {embedding}")
                    
                    print(f"✓ Got {len(embeddings)} embeddings for {clip['title']}")
                    print(f"  Embedding dimensions: {embeddings[0].shape if embeddings else 'None'}")
                    
                except Exception as frame_error:
                    print(f"✗ Frame extraction failed for {clip['title']}: {frame_error}")
            else:
                print(f"✗ File not found at: {local_path}")

        except Exception as e:
            #print(f"✗ Failed to process {clip['title']}: {e}")
            print("failed to download video", )
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

if __name__ == "__main__":
    process_all_clips() 
    # clips = fetch_media_clips()
    # print(clips) 
