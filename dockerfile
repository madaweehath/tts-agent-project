# Dockerfile (Python Agent)
FROM python:3.10-slim

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- IMPROVED COPY STRATEGY ---

# 1. Copy the large, stable model files
# should be removed in favor of using the S3 storage
COPY tts_model /app/tts_model

# 2. !! CRITICAL SECURITY CHANGE !!
# DO NOT COPY CREDENTIALS INTO THE IMAGE. 
# Remove the line below and mount the file as a secret at runtime.
# COPY gcs-credentials.json /app/gcs-credentials.json

# 3. Copy the lightweight application code last
# The source path includes 'full-task/', but the destination is '.' (the /app folder)
# would probably be better to do COPY full-task/* .
COPY full-task/app.py .
COPY full-task/config.py .
COPY full-task/llm_service.py .
COPY full-task/tts_service.py .
COPY full-task/scraper_service.py .
COPY full-task/storage_service.py .

# --- END IMPROVED COPY STRATEGY ---

# Create necessary directories
RUN mkdir -p tts_model/audio_outputs

# Expose port
EXPOSE 8001

# Run the application
# This is CORRECT because app.py was copied directly to the /app directory.
CMD ["python", "app.py"]
