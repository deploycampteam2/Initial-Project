FROM python:3.11-slim

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . /app
WORKDIR /app

CMD ["python", "website/app.py"]
