FROM python:3.10-slim

WORKDIR /app

# Copy only requirements first — enables Docker build caching
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the project
COPY . /app

EXPOSE 8080

CMD ["python", "app.py"]
