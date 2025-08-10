FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libmagic1 \
    libmagic-dev \
    git && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry or pip depending on your setup
COPY pyproject.toml uv.lock ./
COPY .env .env

# Install uv package manager (fast for Python deps)
RUN pip install uv && uv pip install --system .

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
