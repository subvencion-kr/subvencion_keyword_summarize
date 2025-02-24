FROM --platform=linux/amd64 python:3.12-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    openjdk17 \
    g++ \
    make \
    python3-dev \
    musl-dev

# Create and activate virtual environment
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", ". venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000"]
