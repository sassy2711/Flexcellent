FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# System dependencies for OpenCV, MediaPipe, pygame audio, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    libglib2.0-0 \
    libasound2 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the project

COPY . .

# After COPY . .
WORKDIR /app

# Make sure /app is on Python path so 'import backend' works
ENV PYTHONPATH=/app
ENV RUNNING_IN_DOCKER=1
ENV SDL_AUDIODRIVER=dummy

# Default command: run the backend app
CMD ["python", "-m", "backend.main"]


