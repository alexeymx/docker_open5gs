FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install the package
RUN pip install -e .

# Expose the GSUP port
EXPOSE 4222

# Environment variables with defaults
ENV HLR_HOST=0.0.0.0
ENV HLR_PORT=4222
ENV AUTH_SERVICE_URL=http://34.27.10.163:8080
ENV AUTH_SERVICE_TIMEOUT=30
ENV LOG_LEVEL=DEBUG

# Run the service
CMD ["python", "-m", "src.main"] 