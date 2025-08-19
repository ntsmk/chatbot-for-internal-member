## System Requirement

- After logging in as registered user, it allows the user to access /chatbot, otherwise, return 403
- Under /chatbot, the user can type questions, the chatbot returns the answer

## Background

- I noticed our team lacked a strong internal knowledge base to support new employees.
- To address this, I began building a combined internal wiki and a user-friendly AI-powered chatbot.

## Expected user of this system

- Newer ish technician who needs fundamental knowledge?
- Provide step-by-step troubleshooting, link to internal KBs

## Tech Stack

- Backend Development: Python, Flask, RESTful APIs, Flask-Login (authentication), OAuth 2.0 / JWT (security)
- Frontend: Bootstrap (UI/UX)
- Databases: Supabase (PostgreSQL), password hashing for secure account storage
- AI Integration: Google Vertex AI (ML model integration)
- Testing: Pytest (unit & integration testing)
- Deployment & Infrastructure: Docker, GitHub Actions (CI/CD), Google Cloud Run

## Tasks needs to be addressed by order

-   [ ] define the frequent questions and answers for IT support context -> in progress
-   [ ] just prompt engineering might be enough based on it, or fine-tune the model
-   [ ] implement the model in /chatbot
-   [ ] create other routes (should be easier than AI part)

## Status

In development.
