# Dockerfile (Python Agent)
FROM python:3.10-slim

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    espeak-ng \
    libespeak-ng-dev \
    libgomp1 \
    build-essential \
    git \
    curl \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Pre-upgrade pip tooling to avoid build issues
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy app files
COPY full-task/*.py .

# Create necessary directories
RUN mkdir -p tts_model/audio_outputs

# Expose port
EXPOSE 8001

# Run the application
# This is CORRECT because app.py was copied directly to the /app directory.
CMD ["python", "app.py"]
