FROM python:3.11-slim

WORKDIR /app

# System deps needed by ctranslate2/faster-whisper (audio decoding) and cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better Docker layer caching)
COPY Backend/requirements.txt Backend/requirements.txt
RUN pip install --no-cache-dir -r Backend/requirements.txt

# Copy backend source
COPY Backend/ Backend/

EXPOSE 7860

CMD ["uvicorn", "Backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
