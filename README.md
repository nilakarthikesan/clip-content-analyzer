# AI-Powered Content Moderation with Visual Embeddings (CLIP + Supabase)

## 🎥 Project Overview

This project is a production-ready content moderation system that detects inappropriate visual content in media clips using OpenAI's CLIP model. The system features enterprise-grade architecture with class-based design, rate limiting, and comprehensive error handling.

## 🏗️ Architecture

### Class-Based Design (Enterprise Grade)
- **DatabaseManager**: Centralized database operations with connection pooling
- **VideoDownloader**: Rate-limited downloads with progress tracking (5 requests/min)
- **FrameExtractor**: Resource-managed video processing with validation
- **VideoProcessor**: Main orchestrator with dependency injection
- **ProcessingResult**: Structured operation results with metrics

### Database (Supabase)
- **Tech Stack:** Supabase (PostgreSQL + RESTful API)
- **Table:** `media_clips`
  - `id`: UUID – Unique identifier for the clip
  - `title`: Text – Descriptive title of the clip
  - `clip_path`: Text – URL to the media clip in Supabase Storage
  - `source_type`: Text – Source type (e.g., "sports", "movie", "user_uploaded")

### Backend Processing
- **Tech Stack:** Python with class-based architecture
- **Libraries:**
  - `moviepy` for frame extraction
  - `supabase-py` for database operations
  - `requests` with rate limiting for downloads
  - `PIL` for image processing
  - `python-dotenv` for environment management
  - `validators` for input validation
  - `ratelimit` for download throttling

## 🚀 Features

**🔒 Security & Validation:**
- Environment variable-based configuration
- Input validation and sanitization  
- File size and URL validation
- Rate limiting to prevent API abuse

**🏗️ Enterprise Architecture:**
- Class-based design with dependency injection
- Single responsibility principle implementation
- Comprehensive error handling with specific exceptions
- Resource cleanup with context managers

**📊 Monitoring & Analytics:**
- Structured logging with configurable levels
- Processing statistics and success rate tracking
- Download speed monitoring and performance metrics
- System health checks with component validation

**⚡ Performance Features:**
- Rate limiting (5 downloads per minute)
- Progress callbacks for operations
- Connection pooling and session management
- Automatic retry with exponential backoff

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ahluwalij/clip-content-analyzer.git
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
   - Add your Supabase URL and API key to the `.env` file

## 🛠️ Usage

### Main Application (Class-Based)
```bash
python backend/embedding_retrieval/main.py
```

**Features:**
- Comprehensive health checks
- Real-time progress tracking
- Detailed processing summaries
- Error reporting with context

### Legacy Compatibility
```bash
python backend/embedding_retrieval/combined_processor.py
```

**Individual Components:**
- **Configuration:** `config.py` - Environment management
- **Database:** `database_manager.py` - Connection handling  
- **Downloads:** `video_downloader.py` - Rate-limited downloads
- **Frames:** `frame_extractor_class.py` - Video processing
- **Orchestration:** `video_processor.py` - Main workflow

## 📁 Project Structure

```
clip-content-analyzer/
├── backend/
│   └── embedding_retrieval/
│       ├── config.py                    # Configuration management
│       ├── database_manager.py          # Database operations class
│       ├── video_downloader.py          # Rate-limited download class  
│       ├── frame_extractor_class.py     # Frame extraction class
│       ├── video_processor.py           # Main orchestrator class
│       ├── main.py                      # Class-based entry point
│       ├── combined_processor.py        # Legacy entry point
│       ├── supabase_client.py          # Legacy database module
│       ├── frame_extractor.py          # Legacy frame module
│       └── process_clips.py            # Legacy processing module
├── .env.example                         # Environment template
├── .gitignore                          # Git ignore rules
├── requirements.txt                    # Dependencies with rate limiting
└── README.md
```

## ⚙️ Configuration

Environment variables (copy `.env.example` to `.env`):

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anonymous/service key
- `MAX_FILE_SIZE_MB`: Maximum download size (default: 100MB)
- `TEMP_DIR`: Temporary files directory (default: /tmp)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## 🎯 Architecture Benefits

**For Developers:**
- Dependency injection for easy testing
- Clear separation of concerns
- Comprehensive logging and debugging
- Health checks for system validation

**For Operations:**
- Rate limiting prevents API abuse
- Progress tracking for long operations
- Automatic resource cleanup
- Detailed error reporting

**For Scalability:**  
- Modular design for easy extension
- Connection pooling for performance
- Configurable limits and timeouts
- Monitoring and metrics collection

## 🔮 Future Enhancements

- [ ] CLIP model integration for embedding extraction
- [ ] Cosine similarity comparison with flagged keywords
- [ ] Content moderation results in database
- [ ] Web dashboard for management
- [ ] Real-time processing with webhooks
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch  
3. Implement changes with proper testing
4. Follow the class-based architecture patterns
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 