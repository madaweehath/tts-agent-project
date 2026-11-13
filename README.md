
# 3ulum Al-Yawm — AI and TTS Agent

Python service that powers the content-generation pipeline for **3ulum Al-Yawm**, an Arabic news podcast platform. It scrapes Al Riyadh news, rewrites Modern Standard Arabic into conversational Najdi dialect, selects a voice, generates speech, and returns episode data to the backend.

## Project suite

- **AI and TTS agent (this repository):** scraping, LLM processing, speech generation, and media upload
- [Backend](https://github.com/Rmsaah/Arabic_News_Podcast-BE): Spring Boot API, persistence, and pipeline orchestration
- [Frontend](https://github.com/Rmsaah/Arabic_News_Podcast-FE): Angular podcast application
- [Najdi XTTS v2](https://github.com/wasanalmansour480-oss/Najdi-XTTS-v2): model fine-tuning project

## Pipeline

```text
Al Riyadh RSS
    → article scraping
    → seriousness classification
    → Najdi dialect conversion
    → XTTS speech generation
    → Google Cloud Storage
    → episode JSON
```

Serious articles use the `serious` voice. Other articles use the `normal` (lively) voice.

## Features

- Scrapes current Arabic articles from Al Riyadh
- Uses OpenAI models for classification and dialect conversion
- Loads fine-tuned XTTS v2 models from MinIO/S3-compatible storage
- Generates 24 kHz WAV audio with normal and serious voices
- Uploads audio, generated scripts, and source text to Google Cloud Storage
- Exposes individual processing operations and a complete pipeline over HTTP
- Reports LLM, TTS, and storage readiness through a health endpoint

## Requirements

- Python 3.10
- An OpenAI API key
- MinIO or S3-compatible storage containing the XTTS model assets
- Google Cloud service-account credentials for durable pipeline outputs
- A CUDA-capable GPU is strongly recommended; CPU inference is supported but can be slow

## Installation

```bash
git clone https://github.com/madaweehath/tts-agent-project.git
cd tts-agent-project

python -m venv .venv
```

Activate the environment:

```bash
# macOS/Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

Set these environment variables before starting the service:

- `OPENAI_API_KEY` — required for classification and dialect conversion
- `MINIO_ENDPOINT` — defaults to `http://localhost:9000`
- `MINIO_ACCESS_KEY` — defaults to `admin`
- `MINIO_SECRET_KEY` — defaults to `admin`
- `MINIO_BUCKET` — defaults to `temp`
- `MINIO_PREFIX` — defaults to `arabic-news-podcast/tts_model`
- `MINIO_SECURE` — set to `true` for HTTPS; defaults to `false`
- `TTS_S3_CACHE` — optional local model cache directory

PowerShell example:

```powershell
$env:OPENAI_API_KEY = "your_openai_key"
$env:MINIO_ENDPOINT = "http://localhost:9000"
$env:MINIO_ACCESS_KEY = "admin"
$env:MINIO_SECRET_KEY = "your_secret"
$env:MINIO_BUCKET = "temp"
$env:MINIO_PREFIX = "arabic-news-podcast/tts_model"
$env:MINIO_SECURE = "false"
```

The configured prefix must contain the original XTTS vocabulary plus the `lively` and `serious` checkpoints, configurations, and speaker samples expected by `full-task/config.py`.

For Google Cloud Storage, place the service-account file at `full-task/gcs-credentials.json`. The current bucket name is configured in `full-task/config.py`. Do not commit the credentials file.

## Run locally

```bash
cd full-task
python app.py
```

The service starts at `http://localhost:8001`. Model initialization can take time during startup.

Check readiness:

```bash
curl http://localhost:8001/health
```

## API

- `GET /health` — service and dependency readiness
- `GET /api/scrape-news` — scrape current articles
- `POST /api/convert-to-dialect` — convert `{"text": "..."}` to Najdi dialect
- `POST /api/generate-audio` — generate audio from `{"text": "...", "name": "..."}`
- `GET /api/scrape-and-convert` — scrape and convert all returned articles
- `POST /api/scrape-and-process-all` — run the complete pipeline

Example:

```bash
curl -X POST http://localhost:8001/api/scrape-and-process-all
```

The full pipeline returns episode objects that the backend can persist. Uploaded objects use the `audio/`, `scripts/`, and `content/` prefixes.

> Google Cloud credentials are required for durable output URLs. Review storage configuration before running the full pipeline.

## Docker

Build the image:

```bash
docker build -t 3ulum-alyawm-agent .
```

Run it with NVIDIA GPU support and mounted Google Cloud credentials:

```bash
docker run --rm --gpus all -p 8001:8001 \
  -e OPENAI_API_KEY=your_openai_key \
  -e MINIO_ENDPOINT=http://host.docker.internal:9000 \
  -e MINIO_ACCESS_KEY=admin \
  -e MINIO_SECRET_KEY=your_secret \
  -v /absolute/path/gcs-credentials.json:/app/gcs-credentials.json:ro \
  3ulum-alyawm-agent
```

GPU execution requires the NVIDIA Container Toolkit and a compatible driver.

## Source layout

```text
full-task/
├── app.py               # Flask application and endpoints
├── config.py            # Model and storage configuration
├── llm_service.py       # Classification and dialect conversion
├── scraper_service.py   # Al Riyadh scraper
├── tts_service.py       # XTTS model loading and inference
├── storage_service.py   # Google Cloud Storage integration
└── minio_resolver.py    # S3 URI download and local caching
```

