# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TESSERACT_PATH /usr/bin/tesseract
ENV PYTHONPATH .

# Install system dependencies (Tesseract OCR, etc.)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglvnd0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ backend/

# Expose the port
EXPOSE 8000

# Start the application
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
