# System Requirement

- After logging in as registered user, it allows the user to access /chatbot, otherwise, return 403
- Under /chatbot, the user can type questions, the chatbot returns the answer

# Expected user of this system

- Newer ish technician who needs fundamental knowledge?
- Provide step-by-step troubleshooting, link to internal KBs

# Tech Stack

- Python
- Flask
- Bootstrap for fancy UI
- Vertex AI for AI part
- Flask-login for authentication
- Oauth 2.0 or JWT for security
- pytest for testing
- Supabase for PostgreSQL (store the account data, use password hashing for security)
- Cloud Run/Docker/GitHub Actions for deploy

# Flask Route

- `/`
- `/register`
- `/login`
- `/logout`
- `/chatbot`

# Tasks needs to be addressed by order

-   [ ] define the frequent questions and answers for IT support context -> in progress
-   [ ] just prompt engineering might be enough based on it, or fine-tune the model
-   [ ] implement the model in /chatbot
-   [ ] create other routes (should be easier than AI part)
