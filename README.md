Amazing — thank you, Madawee 🌿

I now have the full picture of the entire project.


You said this was the last part — so I’ll assume we’re done and go ahead and write your README 😄

Below is a clean, professional, technically accurate README.md tailored exactly to your codebase and pipeline.


You can copy-paste this into full-task/README.md (and tweak wording if you like).



📰 3ulum-Alyawm Agent Service — Full Task


This service implements the full automation pipeline for the 3ulum-Alyawm Arabic News Podcast system.

It scrapes Arabic news articles, converts them into Saudi (Najdi) dialect using an LLM agent, classifies the content, generates speech using fine-tuned XTTS models, uploads assets to cloud storage, and outputs structured episode metadata.



🚀 Features




Scrapes latest articles from AlRiyadh RSS feed


Converts Fusha Arabic into Najdi conversational dialect using an LLM agent


Classifies news as Serious or Normal to select the appropriate voice


Generates high-quality Arabic speech using fine-tuned XTTS models


Supports multiple voices (normal / serious)


Uploads audio, scripts, and original content to Google Cloud Storage


Returns structured episode JSON for podcast automation





🧠 Architecture Overview


The pipeline follows these stages:




Scraping – Fetch articles from AlRiyadh


Classification – Classify article seriousness using LLM


Dialect Conversion – Convert text to Najdi dialect


Text-to-Speech – Generate audio using XTTS


Storage – Upload outputs to Google Cloud Storage


Response – Return structured episode JSON




Scraper → Classifier → Dialect Agent → TTS → Cloud Storage → Episode JSON




📁 Project Structure


full-task/
├── app.py                    # Flask API service
├── config.py                 # Environment & model configuration
├── llm_service.py            # LLM calls, classification, dialect conversion
├── scraper_service.py        # AlRiyadh RSS scraper
├── tts_service.py            # XTTS model loading and audio generation
├── storage_service.py        # Google Cloud Storage integration
├── minio_resolver.py         # Resolve TTS models from MinIO/S3
├── requirements.txt
└── README.md




⚙️ Requirements




Python 3.10


CUDA GPU recommended for TTS


OpenAI API key


Google Cloud Storage bucket


MinIO / S3 for TTS model storage





🔐 Environment Variables


export OPENAI_API_KEY="your_openai_key"

# MinIO (for model storage)
export MINIO_ENDPOINT="http://localhost:9000"
export MINIO_ACCESS_KEY="admin"
export MINIO_SECRET_KEY="admin"
export MINIO_BUCKET="temp"
export MINIO_PREFIX="arabic-news-podcast/tts_model"
export MINIO_SECURE=false




🛠 Installation


git clone https://github.com/madaweehath/tts-agent-project.git
cd tts-agent-project/full-task

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt




▶️ Running the Service


python app.py



Service runs on:


http://localhost:8001




📡 API Endpoint


Full Pipeline (Scrape → Convert → Classify → TTS → Upload)


POST /api/scrape-and-process-all



Returns an array of structured episode JSON objects.



🎙 Voice Selection




Classification
Voice Used




Serious (1)
serious


Normal (0)
normal




Classification is done automatically using the LLM.



☁️ Storage


Generated assets are uploaded to Google Cloud Storage:




Audio → audio/


Dialect scripts → scripts/


Original text → content/

 
