FROM --platform=linux/amd64 python:3.12

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    openjdk17 \
    g++ \
    make \
    python3-dev \
    musl-dev

# Create and activate virtual environment
RUN python3 -m venv /app/venv

# Upgrade pip and install dependencies
COPY requirements.txt /app/
RUN /app/venv/bin/pip install --upgrade pip setuptools wheel && \
    /app/venv/bin/pip install -r requirements.txt

# Copy application files
COPY . /app

EXPOSE 8000

CMD ["/app/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
