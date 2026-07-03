FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg2-binary \
    python-dotenv \
    alembic \
    pydantic-settings \
    python-multipart \
    passlib[bcrypt] \
    PyJWT \
    pyyaml \
    langgraph \
    langchain \
    langchain-community \
    langchain-core \
    langchain-ollama \
    chromadb \
    sentence-transformers \
    reportlab \
    lxml \
    beautifulsoup4 \
    pymupdf

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]