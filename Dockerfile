FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependencies and install
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy application
COPY . /app

# Expose port (Vercel will provide PORT env var)
EXPOSE 8080

ENV PORT=8080

# Run Streamlit (use sh -c so $PORT expands)
CMD ["sh", "-c", "streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.enableCORS false"]
