FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy processing script
COPY process_pdfs.py .

# Make script executable
RUN chmod +x process_pdfs.py

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set the default command
CMD ["python", "process_pdfs.py"]