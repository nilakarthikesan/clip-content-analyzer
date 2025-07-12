<h1 align="center">
    🎬 AI Clip Content Analyzer
</h1>
<p align="center">
    <p align="center">Enterprise-grade video content moderation with AI-powered frame extraction and analysis</p>
    <br>
</p>

<h4 align="center">
    <a href="#-quick-start">Quick Start</a> | 
    <a href="#-class-based-architecture">Architecture</a> | 
    <a href="#-features">Features</a> | 
    <a href="#-usage">Usage</a>
</h4>

<h4 align="center">
    <a href="https://github.com/ahluwalij/clip-content-analyzer">
        <img src="https://img.shields.io/github/stars/ahluwalij/clip-content-analyzer?style=social" alt="GitHub Stars">
    </a>
    <a href="https://github.com/ahluwalij/clip-content-analyzer/releases">
        <img src="https://img.shields.io/github/v/release/ahluwalij/clip-content-analyzer?style=flat-square" alt="Latest Release">
    </a>
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python" alt="Python Version">
    </a>
    <a href="https://supabase.com/">
        <img src="https://img.shields.io/badge/Database-Supabase-green?style=flat-square&logo=supabase" alt="Supabase">
    </a>
    <a href="https://github.com/ahluwalij/clip-content-analyzer/blob/main/LICENSE">
        <img src="https://img.shields.io/github/license/ahluwalij/clip-content-analyzer?style=flat-square" alt="License">
    </a>
</h4>

---

## 🚀 What This Does

AI Clip Content Analyzer provides:

- **🎯 Intelligent Frame Extraction** - Extract frames at optimal video timestamps (25%, 50%, 75%)
- **⚡ Rate-Limited Downloads** - Respectful API usage with 5 requests/minute throttling  
- **🏗️ Enterprise Architecture** - Class-based design with dependency injection and SOLID principles
- **🔒 Security First** - Input validation, file size limits, and environment-based configuration
- **📊 Comprehensive Monitoring** - Real-time progress tracking, health checks, and detailed analytics
- **🛡️ Robust Error Handling** - Graceful failures with specific exceptions and automatic cleanup

[**🎯 Jump to Quick Start**](#-quick-start) <br>
[**🏗️ Jump to Architecture Guide**](#-class-based-architecture)

> [!IMPORTANT]
> This system requires Python 3.10+ and a Supabase database. Set up your `.env` file before running.

---

## 🚀 Quick Start

<a target="_blank" href="https://github.com/ahluwalij/clip-content-analyzer">
  <img src="https://img.shields.io/badge/Clone-Repository-blue?style=for-the-badge&logo=github" alt="Clone Repository"/>
</a>

```bash
# Clone the repository
git clone https://github.com/ahluwalij/clip-content-analyzer.git
cd clip-content-analyzer

# Install dependencies  
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the application
python backend/embedding_retrieval/main.py
```

### Basic Usage

```python
from video_processor import VideoProcessor
from database_manager import DatabaseManager

# Initialize with dependency injection
processor = VideoProcessor()

# Process all clips from database
results = processor.process_all_clips()

# Check results
for clip_id, result in results.items():
    if result.success:
        print(f"✅ {result.clip_title}: {result.frames_extracted} frames")
    else:
        print(f"❌ {result.clip_title}: {result.error_message}")
```

### Response Format

```python
ProcessingResult(
    clip_id="550e8400-e29b-41d4-a716-446655440000",
    clip_title="Sample Video",
    success=True,
    frames_extracted=3,
    frame_paths=["clip_frame_1.jpg", "clip_frame_2.jpg", "clip_frame_3.jpg"],
    processing_time=12.45,
    error_message=None
)
```

---

## 🏗️ Class-Based Architecture

<div align="center">

| Component | Purpose | Features |
|-----------|---------|----------|
| **🗄️ DatabaseManager** | Database Operations | Connection pooling, health checks, query optimization |
| **⬇️ VideoDownloader** | Rate-Limited Downloads | 5 req/min throttling, progress tracking, session reuse |
| **🎞️ FrameExtractor** | Video Processing | Resource management, validation, multiple extraction modes |
| **🎬 VideoProcessor** | Main Orchestrator | Dependency injection, statistics, health monitoring |
| **📊 ProcessingResult** | Result Objects | Structured feedback, metrics, error context |

</div>

### 🎯 Enterprise Features

```python
# Dependency injection for testing
processor = VideoProcessor(
    database_manager=MockDatabaseManager(),
    video_downloader=MockVideoDownloader(),
    frame_extractor=MockFrameExtractor()
)

# Health checks before processing
health = processor.health_check()
if not all(health.values()):
    logger.error(f"Unhealthy components: {health}")

# Rate limiting with automatic backoff
@sleep_and_retry
@limits(calls=5, period=60)
def download_with_rate_limit(url):
    return requests.get(url)
```

---

## ✨ Features

<div align="center">

### 🔒 **Security & Validation**
Environment variables • Input sanitization • File size limits • Rate limiting

### 🏗️ **Enterprise Architecture** 
Dependency injection • SOLID principles • Resource cleanup • Error handling

### 📊 **Monitoring & Analytics**
Progress tracking • Health checks • Performance metrics • Success rates

### ⚡ **Performance Optimized**
Connection pooling • Automatic retry • Progress callbacks • Session reuse

</div>

---

## 🛠️ Usage

### Class-Based Application (Recommended)

```bash
python backend/embedding_retrieval/main.py
```

**Features:**
- 🏥 Comprehensive health checks
- 📈 Real-time progress tracking  
- 📋 Detailed processing summaries
- 🚨 Error reporting with context

### Legacy Compatibility

```bash
python backend/embedding_retrieval/combined_processor.py
```

### Processing Individual Clips

```python
from video_processor import VideoProcessor

processor = VideoProcessor()

# Process specific clip by ID
result = processor.process_clip_by_id("clip-uuid-here")

if result and result.success:
    print(f"Extracted {result.frames_extracted} frames in {result.processing_time:.2f}s")
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Database Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Processing Limits
MAX_FILE_SIZE_MB=100
TEMP_DIR=/tmp

# Monitoring
LOG_LEVEL=INFO
```

### Supabase Setup

Create a `media_clips` table:

```sql
CREATE TABLE media_clips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    clip_path TEXT NOT NULL,
    source_type TEXT
);
```

---

## 📁 Project Structure

```
clip-content-analyzer/
├── backend/embedding_retrieval/
│   ├── 🆕 main.py                    # Class-based entry point
│   ├── 🆕 database_manager.py        # Database operations class  
│   ├── 🆕 video_downloader.py        # Rate-limited downloads
│   ├── 🆕 frame_extractor_class.py   # Enhanced frame extraction
│   ├── 🆕 video_processor.py         # Main orchestrator
│   ├── config.py                     # Configuration management
│   └── 📁 Legacy modules...          # Backward compatibility
├── .env.example                      # Environment template
├── requirements.txt                  # Dependencies + rate limiting
└── README.md
```

---

## 🎯 Why This Architecture?

<div align="center">

| **For Developers** | **For Operations** | **For Scalability** |
|:---:|:---:|:---:|
| Dependency injection for testing | Rate limiting prevents abuse | Modular design for extension |
| Clear separation of concerns | Progress tracking for ops | Connection pooling for performance |
| Comprehensive debugging | Automatic resource cleanup | Configurable limits & timeouts |
| Health checks for validation | Detailed error reporting | Monitoring & metrics built-in |

</div>

---

## 🔮 Roadmap

- [ ] 🤖 **CLIP Model Integration** - AI-powered content analysis
- [ ] 🎯 **Similarity Scoring** - Cosine similarity for content matching  
- [ ] 🌐 **Web Dashboard** - Real-time monitoring interface
- [ ] 🐳 **Docker Support** - Containerized deployment
- [ ] ☸️ **Kubernetes Ready** - Cloud-native scaling
- [ ] 🔄 **CI/CD Pipeline** - Automated testing & deployment

---

## 🤝 Contributing

<div align="center">

[![Contributors Welcome](https://img.shields.io/badge/Contributors-Welcome-brightgreen?style=for-the-badge)](https://github.com/ahluwalij/clip-content-analyzer/issues)

</div>

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** the class-based architecture patterns
4. **Test** your changes thoroughly  
5. **Submit** a pull request

---

## 📄 License

<div align="center">

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

<br>

**Made with ❤️ for the AI community**

<br>

[![GitHub](https://img.shields.io/badge/GitHub-ahluwalij-black?style=flat-square&logo=github)](https://github.com/ahluwalij)

</div> 