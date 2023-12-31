# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir websocket_client confluent_kafka

# Expose port 443 for WebSocket over HTTPS
EXPOSE 443

# Run your_script.py when the container launches
CMD ["python", "./main.py"]
