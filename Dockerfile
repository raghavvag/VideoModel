FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create temp directory
RUN mkdir -p temp

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV DOWNLOAD_MODELS=true

# Expose port
EXPOSE 8080

# Start the application
CMD gunicorn --bind 0.0.0.0:$PORT api:app
