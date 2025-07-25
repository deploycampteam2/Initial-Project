# Fixed Dockerfile untuk akses localhost
FROM python:3.11-slim

# Set working directory first
WORKDIR /app

# Update pip
RUN pip install --upgrade pip --progress-bar off

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --progress-bar off

# Copy website files to app directory
COPY website/ .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8501

# Run Streamlit with proper settings
CMD ["streamlit", "run", "app.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8501", \
     "--server.headless", "true", \
     "--server.enableCORS", "false", \
     "--server.enableXsrfProtection", "false", \
     "--browser.gatherUsageStats", "false"]