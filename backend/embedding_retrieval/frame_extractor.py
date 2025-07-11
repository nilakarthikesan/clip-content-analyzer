import os
from moviepy import VideoFileClip
from typing import List
import numpy as np
from PIL import Image

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

if __name__ == "__main__":
    # Example usage
    test_video = "path/to/your/video.mp4"
    frames = extract_frames_at_percentages(test_video)
    for i, img in enumerate(frames):
        img.save(f"frame_{i+1}.jpg") 