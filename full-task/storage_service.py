# storage_service.py
import os
import wave
from google.cloud import storage
from config import GCS_CREDENTIALS_PATH, GCS_BUCKET_NAME

# Initialize GCS client
gcs_client = None
try:
    if os.path.exists(GCS_CREDENTIALS_PATH):
        gcs_client = storage.Client.from_service_account_json(GCS_CREDENTIALS_PATH)
        print("✓ Google Cloud Storage client initialized")
    else:
        print("⚠️  GCS credentials not found - files will be saved locally only")
except Exception as e:
    print(f"✗ Error initializing GCS: {e}")

def get_audio_duration(wav_file_path):
    """Calculate duration of WAV file in seconds"""
    try:
        with wave.open(wav_file_path, 'r') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
            return int(duration)  # Return as integer seconds
    except Exception as e:
        print(f"⚠️  Could not calculate duration: {e}")
        return 0

def upload_to_gcs(local_file_path: str, destination_blob_name: str):
    """Upload file to Google Cloud Storage and return public URL"""
    if not gcs_client:
        print("⚠️  GCS client not initialized, returning local path")
        return local_file_path
    
    try:
        bucket = gcs_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        
        # Upload file
        blob.upload_from_filename(local_file_path)
        
        # Make blob publicly accessible (optional - for direct access)
        # blob.make_public()
        
        # Generate public URL
        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{destination_blob_name}"
        
        print(f"✓ Uploaded to GCS: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"❌ Error uploading to GCS: {e}")
        return local_file_path

def cleanup_local_files(*file_paths):
    """Delete local files after upload"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"  🧹 Cleaned up: {file_path}")
        except Exception as e:
            print(f"  ⚠️  Failed to delete {file_path}: {e}")