import os

# ============ LLM Configuration ============
# groq
# API_KEY = "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"
# MODEL_GENERATOR = 'qwen/qwen3-32b'
# MODEL_VALIDATOR = 'qwen/qwen3-32b'

# openai'gpt-4o'
MODEL_GENERATOR = 'gpt-4o-mini'
MODEL_VALIDATOR = 'gpt-4o-mini'
MODEL_CLASSIFIER = 'gpt-4o-mini'
OPENAI_API_KEY = "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"

MAX_RETRIES = 3

# ============ TTS Configuration ============
TTS_MODEL_DIR = "./tts_model" # Base path
TOKENIZER_PATH = os.path.join(TTS_MODEL_DIR, "XTTS_v2.0_original_model_files", "vocab.json")

# --- LIVELY Voice Configuration ---
LIVELY_CHECKPOINT_PATH = os.path.join(TTS_MODEL_DIR, "lively", "best_model-001.pth")
LIVELY_CONFIG_PATH = os.path.join(TTS_MODEL_DIR, "lively", "config.json")
LIVELY_SPEAKER_REFERENCE = os.path.join(TTS_MODEL_DIR, "lively", "sample_513.wav")

# --- SERIOUS Voice Configuration ---
SERIOUS_CHECKPOINT_PATH = os.path.join(TTS_MODEL_DIR, "serious", "best_model-001.pth")
SERIOUS_CONFIG_PATH = os.path.join(TTS_MODEL_DIR, "serious", "config.json")
SERIOUS_SPEAKER_REFERENCE = os.path.join(TTS_MODEL_DIR, "serious", "sample_691.wav")

OUTPUT_DIR = os.path.join(TTS_MODEL_DIR, "audio_outputs")
# ============ Google Cloud Storage Configuration ============
GCS_CREDENTIALS_PATH = "./gcs-credentials.json"
GCS_BUCKET_NAME = "arabic-news-podcast-storage"