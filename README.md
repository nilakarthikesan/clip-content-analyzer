# AI-Powered Content Moderation with Visual Embeddings (CLIP + Supabase)

## 🎥 Project Overview

This project is a full-stack content moderation system that detects inappropriate visual content in media clips using OpenAI's CLIP model. The system stores video metadata in a Supabase database, extracts visual embeddings from each clip, compares them against textual embeddings of flagged keywords (e.g., "blood", "violence"), and returns a content warning when inappropriate content is detected.

## 🧠 System Architecture

### 1. Database (Supabase)
- **Tech Stack:** Supabase (PostgreSQL + RESTful API)
- **Table:** `media_clips`
  - `id`: UUID – Unique identifier for the clip
  - `title`: Text – Descriptive title of the clip
  - `clip_path`: Text – URL to the media clip in Supabase Storage
  - `source_type`: Text – Source type (e.g., "sports", "movie", "user_uploaded")

### 2. Backend Processing
- **Tech Stack:** Python
- **Libraries:**
  - `moviepy` to extract frames from video
  - `supabase-py` to connect to database
  - `requests` to download videos from URLs
  - `PIL` for image processing

## 🚀 Features

- **Frame Extraction:** Extracts frames at 25%, 50%, and 75% of video duration
- **Database Integration:** Connects to Supabase to fetch video metadata
- **Temporary File Management:** Downloads videos to temp files, processes them, and cleans up
- **Modular Design:** Separate functions for different processing steps
- **Content Moderation:** CLIP-based detection of inappropriate content using text-image similarity
- **Multi-category Detection:** Violence, sexual content, drugs, hate speech, self-harm
- **Configurable Sensitivity:** Adjustable similarity thresholds for content flagging
- **Detailed Reporting:** JSON reports with similarity scores and category breakdowns

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd clip-content-analyzer
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Supabase:**
   - Create a Supabase project
   - Create a `media_clips` table with the schema above
   - Upload videos to Supabase Storage
   - Update the `clip_path` column with public URLs

4. **Configure the application:**
   - Update `SUPABASE_URL` and `SUPABASE_KEY` in `backend/embedding_retrieval/combined_processor.py`

## 🛠️ Usage

### Process All Clips with Content Moderation
```bash
python backend/embedding_retrieval/combined_processor.py
```

This will:
1. Connect to your Supabase database
2. Fetch all video clips
3. Download each video to a temporary file
4. Extract 3 frames (at 25%, 50%, 75% of duration)
5. Generate CLIP embeddings for each frame
6. Compare embeddings with inappropriate content keywords
7. Save moderation results to JSON files
8. Clean up temporary files

### Test Content Moderation System
```bash
python backend/embedding_retrieval/test_moderation.py
```

This will run tests to demonstrate the content moderation functionality.

### Content Moderation Configuration

#### Adjusting Sensitivity
```python
from content_moderator import ContentModerator

# Set similarity threshold (0.0 to 1.0, higher = more strict)
moderator.set_similarity_threshold(0.8)  # Default is 0.7
```

#### Adding Custom Words
```python
# Add words to existing categories
moderator.add_inappropriate_word("violence", "knife attack")
moderator.add_inappropriate_word("violence", "street fight")

# Add new categories
moderator.add_inappropriate_word("custom_category", "inappropriate word")
```

### Individual Components

- **Database Connection:** `supabase_client.py`
- **Frame Extraction:** `frame_extractor.py`
- **Video Processing:** `process_clips.py`

## 📁 Project Structure

```
clip-content-analyzer/
├── backend/
│   └── embedding_retrieval/
│       ├── combined_processor.py   # Main processor with content moderation
│       ├── content_moderator.py    # ContentModerator class
│       ├── test_moderation.py      # Test script for moderation
│       ├── supabase_client.py      # Database connection
│       ├── frame_extractor.py      # Frame extraction logic
│       └── process_clips.py        # Video processing pipeline
├── requirements.txt                # Python dependencies
├── .gitignore
└── README.md
```

## 🔮 Future Enhancements

- [x] CLIP model integration for embedding extraction
- [x] Cosine similarity comparison with flagged keywords
- [x] Content moderation results stored in JSON files
- [ ] Content moderation results stored in database
- [ ] Web dashboard for viewing flagged content
- [ ] Real-time processing with webhooks
- [ ] Confidence scoring for moderation results
- [ ] Batch processing for large datasets
- [ ] Custom model fine-tuning for specific content types

## 🛡️ Content Moderation Categories

The system detects inappropriate content across multiple categories:

### Violence
- violence, fight, fighting, attack, assault, battle, war, combat
- blood, bloody, gore, injury, wound, bruise, cut, stab, shoot
- gun, rifle, pistol, weapon, knife, sword, bomb, explosion
- death, dead, corpse, murder, kill, killing, homicide

### Sexual Content
- nude, naked, sexual, pornographic, explicit, adult content
- intimate, provocative, suggestive

### Drugs
- drugs, cocaine, heroin, marijuana, weed, alcohol abuse
- substance abuse, illegal drugs, drug paraphernalia

### Hate Speech
- hate, racist, discrimination, offensive, slur, bigotry
- extremist, terrorist, hate speech

### Self-Harm
- self harm, suicide, cutting, self injury, self mutilation

## 📊 Output Format

The system generates detailed JSON reports for each processed clip:

```json
{
  "clip_id": "123",
  "clip_title": "Sample Video",
  "frames_analyzed": 3,
  "moderation_results": [
    {
      "frame": 1,
      "filename": "123_frame_1.jpg",
      "moderation": {
        "flagged": false,
        "max_similarity": 0.45,
        "most_similar_content": "peaceful",
        "categories": {
          "violence": {
            "max_similarity": 0.23,
            "most_similar_word": "fight",
            "flagged": false
          },
          "sexual": {
            "max_similarity": 0.12,
            "most_similar_word": "intimate",
            "flagged": false
          }
        }
      }
    }
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 