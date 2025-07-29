FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 5006

# Run the application
CMD ["panel", "serve", "panel_air_quality_dashboard.py", "--address", "0.0.0.0", "--port", "5006", "--allow-websocket-origin=*"] 