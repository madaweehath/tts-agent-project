

# 📰 3ulum-Alyawm Agent Service — Full Task

This service implements the full automation pipeline for the **3ulum-Alyawm Arabic News Podcast system**.  
It scrapes Arabic news articles, converts them into Saudi (Najdi) dialect using an LLM agent, classifies the content, generates speech using fine-tuned XTTS models, uploads assets to cloud storage, and outputs structured episode metadata.

---

## 🚀 Features

- Scrapes latest articles from **AlRiyadh RSS feed**
- Converts Fusha Arabic into **Najdi conversational dialect** using an LLM agent
- Classifies news as **Serious** or **Normal** to select the appropriate voice
- Generates high-quality Arabic speech using **fine-tuned XTTS models**
- Supports **multiple voices** (normal / serious)
- Uploads audio, scripts, and original content to **Google Cloud Storage**
- Returns structured episode JSON for podcast automation

---

## 🧠 Architecture Overview

The pipeline follows these stages:

1. Scraping – Fetch articles from AlRiyadh  
2. Classification – Classify article seriousness using LLM  
3. Dialect Conversion – Convert text to Najdi dialect  
4. Text-to-Speech – Generate audio using XTTS  
5. Storage – Upload outputs to Google Cloud Storage  
6. Response – Return structured episode JSON  

```

Scraper → Classifier → Dialect Agent → TTS → Cloud Storage → Episode JSON

```

---

## 📁 Project Structure

```

full-task/
├── app.py
├── config.py
├── llm_service.py
├── scraper_service.py
├── tts_service.py
├── storage_service.py
├── minio_resolver.py
├── requirements.txt
└── README.md

````

---

## ⚙️ Requirements

- Python 3.10
- CUDA GPU recommended for TTS
- OpenAI API key
- Google Cloud Storage bucket
- MinIO / S3 for TTS model storage

---

## 🔐 Environment Variables

```bash
export OPENAI_API_KEY="your_openai_key"

export MINIO_ENDPOINT="http://localhost:9000"
export MINIO_ACCESS_KEY="admin"
export MINIO_SECRET_KEY="admin"
export MINIO_BUCKET="temp"
export MINIO_PREFIX="arabic-news-podcast/tts_model"
export MINIO_SECURE=false
````

---

## 🛠 Installation

```bash
git clone https://github.com/madaweehath/tts-agent-project.git
cd tts-agent-project/full-task

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## ▶️ Running the Service

```bash
python app.py
```

Service runs at:

```
http://localhost:8001
```

---

## 📡 API Endpoint


### Full Pipeline

```
POST /api/scrape-and-process-all
```

Returns structured episode JSON objects.

---

## 🎙 Voice Selection

| Classification | Voice   |
| -------------- | ------- |
| Serious (1)    | serious |
| Normal (0)     | normal  |

---

## ☁️ Storage

Assets are uploaded to Google Cloud Storage:

* Audio → `audio/`
* Scripts → `scripts/`
* Original → `content/`

If GCS is unavailable, files are stored locally:

```
./tts_model/audio_outputs
```

---

### 🐳 Docker Support

This service includes a Dockerfile for building a self-contained runtime environment with all system and Python dependencies required for Arabic TTS generation.

The image is based on `python:3.10-slim` and installs:

* Audio processing libraries (`ffmpeg`, `libsndfile`, `espeak-ng`)
* Build tools for native dependencies
* GPU-enabled PyTorch (CUDA 13.0 wheels)

The container exposes port `8001` and runs the application using `app.py`.

#### Build the image

```bash
docker build -t tts-agent .
```

#### Run the container

```bash
docker run -p 8001:8001 --gpus all tts-agent
```

> ⚠️ GPU support requires Docker with NVIDIA runtime enabled.

