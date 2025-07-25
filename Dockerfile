# Simple Dockerfile untuk Ubuntu 16.04 compatibility
FROM python:3.9-slim

# Update pip dengan no-progress untuk avoid threading issue
RUN pip install --upgrade pip --progress-bar off

# Set working directory
WORKDIR /app

# Copy requirements file
COPY website/requirements.txt .

# Install dependencies with minimal progress output
RUN pip install --no-cache-dir -r requirements.txt --progress-bar off

# Copy website folder
COPY website/ .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit with optimized settings for Ubuntu 16.04
CMD ["streamlit", "run", "app.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8501", \
     "--server.headless", "true", \
     "--server.enableCORS", "false", \
     "--server.enableXsrfProtection", "false", \
     "--browser.gatherUsageStats", "false"]