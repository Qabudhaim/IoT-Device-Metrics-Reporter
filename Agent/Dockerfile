# Use a lightweight Python base image
FROM python:3.12-slim

# Install iproute2 
RUN apt-get update && apt-get install -y iproute2 && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy all project files
COPY . /app

# Install dependencies if requirements.txt exists
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the script
CMD ["python", "main.py"]