import os

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")  # minio api endpoint
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin") # the username for minio, it should be included in the environment variables for both local and the deployed apps
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "admin") # the password for minio, it should be included in the environment variables for both local and the deployed apps
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "temp") # the bucket name that was chosen
MINIO_PREFIX = os.getenv("MINIO_PREFIX", "arabic-news-podcast/tts_model") # this is the prefix for the files in the bucket, which is the directory under the bucket
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"  # set true if using https

# ============ LLM Configuration ============
# groq
# key is exposed, regenerate and populate from an environment variable
# API_KEY = "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"
# MODEL_GENERATOR = 'qwen/qwen3-32b'
# MODEL_VALIDATOR = 'qwen/qwen3-32b'

# openai'gpt-4o'
MODEL_GENERATOR = 'gpt-4o-mini'
MODEL_VALIDATOR = 'gpt-4o-mini'
MODEL_CLASSIFIER = 'gpt-4o-mini'
# key is exposed, regenerate and populate from an environment variable
OPENAI_API_KEY = "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"

MAX_RETRIES = 3

# ============ TTS Configuration ============
TTS_MODEL_DIR = f"s3://{MINIO_BUCKET}/{MINIO_PREFIX}"
TOKENIZER_PATH = f"{TTS_MODEL_DIR}/XTTS_v2.0_original_model_files/vocab.json"

# --- LIVELY Voice Configuration ---
LIVELY_CHECKPOINT_PATH = f"{TTS_MODEL_DIR}/lively/best_model.pth"
LIVELY_CONFIG_PATH = f"{TTS_MODEL_DIR}/lively/config.json"
LIVELY_SPEAKER_REFERENCE = f"{TTS_MODEL_DIR}/lively/sample_513.wav"

# --- SERIOUS Voice Configuration ---
SERIOUS_CHECKPOINT_PATH = f"{TTS_MODEL_DIR}/serious/best_model.pth"
SERIOUS_CONFIG_PATH = f"{TTS_MODEL_DIR}/serious/config.json"
SERIOUS_SPEAKER_REFERENCE = f"{TTS_MODEL_DIR}/serious/sample_691.wav"

OUTPUT_DIR = os.path.join("./tts_model", "audio_outputs")
# ============ Google Cloud Storage Configuration ============
GCS_CREDENTIALS_PATH = "./gcs-credentials.json"
GCS_BUCKET_NAME = "arabic-news-podcast-storage"
