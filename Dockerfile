# ReelForge AI Docker Container Specification
FROM python:3.11-slim

# Install system video dependencies (FFmpeg, OpenCV, fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency list and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose Web Dashboard Port
EXPOSE 8000

# Start ReelForge AI Server & Autonomous Scheduler Daemon
CMD ["python", "-m", "reelforge.server"]
