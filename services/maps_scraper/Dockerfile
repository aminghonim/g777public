FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN useradd -m -u 1001 scraperuser

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy root requirements first for access to shared libs if any
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code (context will be root)
COPY . .

# Ensure data directory exists and is writable
RUN mkdir -p /app/data && chown -R scraperuser:scraperuser /app

USER scraperuser

EXPOSE 8000

RUN playwright install chromium

# Fixed command to run from the service subdirectory
CMD ["uvicorn", "services.maps_scraper.maps_api:app", "--host", "0.0.0.0", "--port", "8000"]
