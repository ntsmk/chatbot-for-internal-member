FROM python:3.10-slim

WORKDIR /chatbot

# Copy only requirements first — enables Docker build caching
COPY requirements.txt /chatbot/

RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the project
COPY . /chatbot

EXPOSE 8080

CMD ["python", "engine.py"]
