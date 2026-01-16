FROM python:3.10-slim

WORKDIR /chatbot

# Copy only requirements first — enables Docker build caching
COPY requirements.txt /chatbot/

RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the project
COPY . /chatbot

ENV PORT=8080
ENV GOOGLE_AI_API_KEY=""
ENV GCP_PROJECT_ID=""
ENV SUPABASE_URL=""
ENV SUPABASE_SERVICE_KEY=""
EXPOSE 8080

CMD ["python", "app.py"]
