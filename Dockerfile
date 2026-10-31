# Use an official lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system utilities needed for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definitions first (layer caching)
COPY requirements.txt .

# Install dependencies (CPU-only PyTorch optimization prevents multi-GB GPU downloads)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and documents
COPY . .

# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Set the default entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Default command runs the FastAPI backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]