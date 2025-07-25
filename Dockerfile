FROM python:3.11-slim

RUN pip install --upgrade pip --progress-bar off --no-deps

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY .
WORKDIR /app

# Expose port
EXPOSE 8501

# Run with minimal settings
CMD ["streamlit", "run", "app.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8501", \
     "--server.headless", "true", \
     "--browser.gatherUsageStats", "false"]