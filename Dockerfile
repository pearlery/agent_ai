FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY agntics_ai/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agntics_ai/ ./agntics_ai/
COPY .env.example ./.env

# Create data directory
RUN mkdir -p /app/data

# Expose ports for Web App and Control Agent
EXPOSE 5000 9004

# Health check for both services
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5000/health || curl -f http://localhost:9004/health || exit 1

# Run the integrated application with Control Agent and Web App
CMD ["python", "-m", "agntics_ai.cli.run_all", "--docker"]