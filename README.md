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
  - `python-dotenv` for environment variable management
  - `validators` for URL validation

## 🚀 Features

- **Secure Configuration:** Environment variable-based configuration
- **Frame Extraction:** Extracts frames at 25%, 50%, and 75% of video duration
- **Database Integration:** Connects to Supabase to fetch video metadata
- **Temporary File Management:** Downloads videos to temp files, processes them, and cleans up
- **Input Validation:** URL validation and file size limits
- **Comprehensive Logging:** Structured logging with configurable levels
- **Error Handling:** Robust error handling with specific exception types
- **Modular Design:** Separate modules for different processing steps

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

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your actual values
   ```

4. **Set up Supabase:**
   - Create a Supabase project
   - Create a `media_clips` table with the schema above
   - Upload videos to Supabase Storage
   - Update the `clip_path` column with public URLs
   - Add your Supabase URL and API key to the `.env` file

## 🛠️ Usage

### Process All Clips
```bash
python backend/embedding_retrieval/combined_processor.py
```

This will:
1. Connect to your Supabase database
2. Fetch all video clips
3. Download each video to a temporary file (with size validation)
4. Extract 3 frames (at 25%, 50%, 75% of duration)
5. Save frames as images
6. Clean up temporary files
7. Generate detailed logs and processing summary

### Individual Components

- **Configuration:** `config.py` - Centralized configuration management
- **Database Connection:** `supabase_client.py` - Secure database operations
- **Frame Extraction:** `frame_extractor.py` - Video frame extraction with validation
- **Video Processing:** `process_clips.py` - Complete processing pipeline

## 📁 Project Structure

```
clip-content-analyzer/
├── backend/
│   └── embedding_retrieval/
│       ├── config.py               # Configuration management
│       ├── supabase_client.py      # Database connection
│       ├── frame_extractor.py      # Frame extraction logic
│       ├── process_clips.py        # Video processing pipeline
│       └── combined_processor.py   # Main application entry point
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
└── README.md
```

## ⚙️ Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and set the following:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anonymous/service key
- `MAX_FILE_SIZE_MB`: Maximum file size for downloads (default: 100MB)
- `TEMP_DIR`: Directory for temporary files (default: /tmp)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## 🔮 Future Enhancements

- [ ] CLIP model integration for embedding extraction
- [ ] Cosine similarity comparison with flagged keywords
- [ ] Content moderation results stored in database
- [ ] Web dashboard for viewing flagged content
- [ ] Real-time processing with webhooks
- [ ] Confidence scoring for moderation results
- [ ] Unit and integration tests
- [ ] Docker containerization
- [ ] CI/CD pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 