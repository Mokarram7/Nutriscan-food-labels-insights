# Use official Python slim image
FROM python:3.10-slim

# Install system dependencies and Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port for Render
EXPOSE 8000

# Run the Django app with gunicorn
CMD ["gunicorn", "ocr_project_pr1.wsgi:application", "--bind", "0.0.0.0:8000"]
