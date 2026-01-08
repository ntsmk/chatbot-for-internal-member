# FAQ Chatbot for internal member 

## Background

- I noticed our team lacked a strong internal knowledge base to support new employees.
- To address this, I began building a combined internal wiki and a user-friendly AI-powered chatbot.

## Expected user of this system

- Newer technician who needs fundamental knowledge
- Provide step-by-step troubleshooting, link to internal KBs

## Tech Stack

- Backend Development: Python, Flask, RESTful APIs
- Frondend Development: HTML5, CSS3, JavaScript (DOM manipulation, event handling, async fetch API)
- DB: Supabase, Postgres for vector DB
- AI Integration: Google Vertex AI (prompt engineering + RAG)
- Testing: Pytest (unit & integration testing)
- DevOps & Infrastructure: Docker, GitHub Actions (CI/CD), Terraform, Google Cloud Run
- Security & Secrets Management: GitHub Secrets for API credentials and environment variables
- Observability: Cloud Logging & Monitoring (GCP)

## Architecture diagram
<img src="images/diagram_v1.png" alt="Alt text" width="800"/>


## Tasks needs to be addressed by order

-   [X] Define the frequent questions and answers for IT support context -> internal wiki created. Defined the frequent questions and answers. -> Done
-   [X] Just prompt engineering might be enough based on it, or fine-tune the model -> prompt engineering + RAG used -> Done
-   [X] Deploy the model in /chatbot as simple MVP -> Done


## Screenshot
<img src="images/screenshot_v1.jpg" alt="Alt text" width="800"/>
