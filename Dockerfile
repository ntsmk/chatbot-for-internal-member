# Use an official Python image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the app files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 8080

# Run the Flask app
CMD ["python", "app.py"]
