FROM python:3.11-slim

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

# Expose Streamlit port
EXPOSE 8501

# Change to website directory and run Streamlit
WORKDIR /app/website
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.headless", "true"]