import os

# ============ LLM Configuration ============
# groq
# API_KEY = "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"
# MODEL_GENERATOR = 'qwen/qwen3-32b'
# MODEL_VALIDATOR = 'qwen/qwen3-32b'

# openai'gpt-4o'
MODEL_GENERATOR = 'gpt-3.5-turbo'
MODEL_VALIDATOR = 'gpt-3.5-turbo'
OPENAI_API_KEY = "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"

MAX_RETRIES = 3

# ============ TTS Configuration ============
TTS_MODEL_DIR = "tts_model"
CHECKPOINT_PATH = os.path.join(TTS_MODEL_DIR, "checkpoint_files", "best_model.pth")
CONFIG_PATH = os.path.join(TTS_MODEL_DIR, "checkpoint_files", "config.json")
TOKENIZER_PATH = os.path.join(TTS_MODEL_DIR, "XTTS_v2.0_original_model_files", "vocab.json")
SPEAKER_REFERENCE = os.path.join(TTS_MODEL_DIR, "sample_83.wav")
OUTPUT_DIR = os.path.join(TTS_MODEL_DIR, "audio_outputs")

# ============ Google Cloud Storage Configuration ============
GCS_CREDENTIALS_PATH = "./gcs-credentials.json"
GCS_BUCKET_NAME = "arabic-news-podcast-storage"