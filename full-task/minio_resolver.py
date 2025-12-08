import os
import hashlib
from pathlib import Path
from urllib.parse import urlparse
from minio import Minio
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE

_client = Minio(
    MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)

CACHE_DIR = Path(os.getenv("TTS_S3_CACHE", ".cache/tts-model")).resolve()
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cache_path_for_uri(uri: str) -> Path:
    parsed = urlparse(uri)
    key = parsed.path.lstrip("/")
    h = hashlib.sha256(uri.encode("utf-8")).hexdigest()[:8]
    return CACHE_DIR / f"{key}.{h}"

def resolve_path(path_or_uri: str) -> str:
    if not path_or_uri or not isinstance(path_or_uri, str):
        return path_or_uri
    if path_or_uri.startswith("s3://"):
        parsed = urlparse(path_or_uri)
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")
        local_path = _cache_path_for_uri(path_or_uri)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        if not local_path.exists():
            _client.fget_object(bucket, key, str(local_path))
        return str(local_path)
    return path_or_uri
