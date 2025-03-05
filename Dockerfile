# Build stage
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies and certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    git \
    ca-certificates \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Update certificates and set SSL configuration
RUN update-ca-certificates
ENV SSL_CERT_DIR=/etc/ssl/certs
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Copy only requirements
COPY requirements.txt .

# Install dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Create model directory
RUN mkdir -p /opt/models/clip

# Download model files with proper SSL configuration
RUN curl -k -L https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/config.json -o /opt/models/clip/config.json && \
    curl -k -L https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/preprocessor_config.json -o /opt/models/clip/preprocessor_config.json

# Alternative: Use wget instead of curl
RUN apt-get update && apt-get install -y wget && \
    wget --no-check-certificate https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/pytorch_model.bin -O /opt/models/clip/pytorch_model.bin && \
    apt-get remove -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Final stage
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/models /opt/models
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV TRANSFORMERS_CACHE="/opt/models"
ENV HF_HOME="/opt/models"
ENV TORCH_HOME="/opt/models"
ENV SSL_CERT_DIR=/etc/ssl/certs
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Copy only necessary files
COPY ./api ./api
COPY ./agents ./agents
COPY ./database ./database
COPY ./main.py .
COPY ./config.py .
COPY ./schemas.py .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"] 