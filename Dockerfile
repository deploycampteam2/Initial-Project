FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies + fix GPG error
RUN apt-get update && \
    apt-get install -y --no-install-recommends gnupg curl && \
    # Tambahkan GPG key dari Debian keyring
    for key in \
        0E98404D386FA1D9 \
        6ED0E7B82643E131 \
        F8D2585B8783D481 \
        54404762BBB6E853 \
        BDE6D2B9216EC7A8; do \
        gpg --keyserver keyserver.ubuntu.com --recv-keys "$key" && \
        gpg --export --armor "$key" | apt-key add -; \
    done && \
    # Update lagi setelah key ditambahkan
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libffi-dev \
        libpq-dev \
        libssl-dev \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
