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

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd clip-content-analyzer
   ```

2. **Install Python dependencies:**
   ```bash
   pip install supabase moviepy requests pillow numpy
   ```

3. **Set up Supabase:**
   - Create a Supabase project
   - Create a `media_clips` table with the schema above
   - Upload videos to Supabase Storage
   - Update the `clip_path` column with public URLs

4. **Configure the application:**
   - Update `SUPABASE_URL` and `SUPABASE_KEY` in `backend/embedding_retrieval/combined_processor.py`

## 🛠️ Usage

### Process All Clips
```bash
python backend/embedding_retrieval/combined_processor.py
```

This will:
1. Connect to your Supabase database
2. Fetch all video clips
3. Download each video to a temporary file
4. Extract 3 frames (at 25%, 50%, 75% of duration)
5. Save frames as images
6. Clean up temporary files

### Individual Components

- **Database Connection:** `supabase_client.py`
- **Frame Extraction:** `frame_extractor.py`
- **Video Processing:** `process_clips.py`

## 📁 Project Structure

```
clip-content-analyzer/
├── backend/
│   └── embedding_retrieval/
│       ├── supabase_client.py      # Database connection
│       ├── frame_extractor.py      # Frame extraction logic
│       ├── process_clips.py        # Video processing pipeline
│       └── combined_processor.py   # All-in-one processor
├── .gitignore
└── README.md
```

## 🔮 Future Enhancements

- [ ] CLIP model integration for embedding extraction
- [ ] Cosine similarity comparison with flagged keywords
- [ ] Content moderation results stored in database
- [ ] Web dashboard for viewing flagged content
- [ ] Real-time processing with webhooks
- [ ] Confidence scoring for moderation results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 