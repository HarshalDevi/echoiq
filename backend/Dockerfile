# Small base with Python + ffmpeg
FROM python:3.11-slim

# Install ffmpeg & runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt /app/requirements.txt

# Install Python deps
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY . /app

# Expose port used by Render
ENV PORT=10000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
