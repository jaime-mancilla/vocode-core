FROM python:3.10-slim

# Install build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libssl-dev \
    libffi-dev \
    rustc \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

# Set the command to run your app
CMD ["uvicorn", "apps.telephony_app.main:app", "--host", "0.0.0.0", "--port", "10000"]
