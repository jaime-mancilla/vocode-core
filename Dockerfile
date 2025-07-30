# Use a smaller Python base image
FROM python:3.10-slim

# Install only what's truly required to build packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Pre-copy only requirements.txt to utilize Docker caching
COPY requirements.txt .

# Upgrade pip and install dependencies without cache
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the project
COPY . .

# Run the application
CMD ["uvicorn", "apps.telephony_app.main:app", "--host", "0.0.0.0", "--port", "10000"]
