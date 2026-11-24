FROM python:3.7-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the live package in development mode
RUN pip install -e .

# Run tests by default
CMD ["pytest", "tests/", "-v"]
