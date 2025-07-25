# Use Python 3.9 for better Ubuntu 16.04 compatibility
FROM python:3.9-slim

# Install UV
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy UV configuration files
COPY pyproject.toml .
COPY .python-version .

# Copy website folder
COPY website/ ./website/

# Install dependencies with UV
RUN uv sync

# Create non-root user for better security and thread handling
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose Streamlit port
EXPOSE 8501

# Change to website directory and run Streamlit with optimized settings
WORKDIR /app/website
CMD ["uv", "run", "streamlit", "run", "app.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8501", \
     "--server.headless", "true", \
     "--server.enableCORS", "false", \
     "--server.enableXsrfProtection", "false", \
     "--browser.gatherUsageStats", "false"]