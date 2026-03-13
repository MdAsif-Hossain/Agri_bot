# --- Stage 1: Build React Frontend ---
    FROM node:20-alpine AS frontend-builder
    WORKDIR /app/frontend
    
    COPY frontend/package*.json ./
    RUN npm ci
    
    COPY frontend/ ./
    RUN npm run build
    
    # --- Stage 2: Python Backend ---
    FROM python:3.11-slim
    
    WORKDIR /app
    
    # Install system dependencies
    RUN apt-get update && apt-get install -y \
        build-essential \
        ffmpeg \
        git \
        && rm -rf /var/lib/apt/lists/*
    
    # Install Python dependencies
    COPY requirements.txt .
    # Setup for llama-cpp-python
    ENV CMAKE_ARGS="-DLLAMA_NATIVE=OFF"
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Copy project files
    COPY . .
    
    # Copy built frontend from Stage 1
    COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
    
    # Expose API port
    EXPOSE 8000
    
    # Run the application
    CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
    
