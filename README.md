Email Task Report Automation System
A local-first automation system that converts daily work logs into structured, professional email reports and sends them automatically via Gmail.
The application uses a locally running LLM through Ollama, provides a Streamlit-based UI, and is fully containerized using Docker.
Overview
This system is designed to remove the repetitive effort of writing daily status emails.
You provide a short work log in natural language along with the recipient’s email address. The application handles task extraction, formatting, email generation, and delivery.
All AI processing runs locally. No external LLM APIs are used.
How It Works
User enters a work log in plain text
Recipient email and task list are extracted
Tasks are structured into a professional report
A local LLM generates an HTML email
Email is sent via Gmail SMTP
User receives a preview and confirmation
Features
Natural language work log input
Automatic recipient and task extraction
HTML email generation using a local LLM
Multiple tone options (formal, neutral, friendly)
Gmail SMTP integration using app passwords
Fallback template-based email generation
Fully Dockerized deployment
No external AI or third-party data sharing
Tech Stack
Frontend
Streamlit
Custom CSS
Backend
Python 3.11
LangChain
Regex-based parsing logic
LLM Runtime
Ollama
Llama 3.1 (8B)
Email
smtplib
email.mime
Gmail SMTP with TLS
Deployment
Docker
docker-compose
Project Structure
Email Automation System/
├── app/
│   ├── app.py
│   ├── config.py
│   ├── data/
│   ├── modules/
│   │   ├── email_auth.py
│   │   ├── email_sender.py
│   │   ├── prompt_parser.py
│   │   └── report_generator.py
│   └── prompts/
├── scripts/
│   ├── evaluate_parser.py
│   │── generate_dataset.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
└── .gitignore
Prerequisites
macOS
Docker Desktop
Ollama installed locally
Gmail account with:
Two-factor authentication enabled
App password generated
Setup
Clone the Repository
git clone https://github.com/your-username/email-automation-system.git
cd "Email Automation System"
Install and Run Ollama
ollama pull llama3.1:8b
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
Verify that Ollama is running:
curl http://localhost:11434/api/tags
Build and Run with Docker
docker-compose build
docker-compose up -d
docker logs -f task-report-automation
The application will be available at:
http://localhost:8501
Gmail App Password Setup
Gmail requires app passwords when two-factor authentication is enabled.
Visit https://myaccount.google.com/apppasswords
Create a new app password with a custom name
Copy the 16-character password (no spaces)
Using the Application
Configure Email Credentials
Enter your Gmail address
Enter the Gmail app password
Credentials are stored only in Streamlit session state
Enter a Work Log
Example input:
Send to: manager@company.com

Today's tasks:
- Fixed critical navigation bug
- Implemented analytics dashboard
- Attended sprint planning meeting
- Started authentication module
Required elements:
A line indicating the recipient email
A list or description of tasks
Generate and Send
Available actions:
Preview Only: Generate the email without sending
Generate & Send: Generate and send the email
The app displays:
Recipient
Subject
Task count
Generation method (LLM or fallback)
HTML preview
Core Modules
prompt_parser.py
Extracts recipient email from input text
Identifies task lines using bullets, numbering, and headers
Outputs a clean list of tasks
report_generator.py
Connects to Ollama using environment configuration
Builds structured prompts for the LLM
Validates and cleans generated HTML
Falls back to a deterministic template when needed
email_sender.py
Sends multipart (text and HTML) emails
Uses Gmail SMTP with TLS
Handles authentication and delivery logging
email_auth.py
Stores credentials in Streamlit session state
Does not persist sensitive data to disk
Configuration
Environment variables provided via docker-compose.yml:
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1:8b
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
Running Without Docker (Optional)
pip install -r requirements.txt
export OLLAMA_HOST=http://127.0.0.1:11434
ollama serve
streamlit run app/app.py
Troubleshooting
LLM Connection Issues
Ensure ollama serve is running
Verify OLLAMA_HOST configuration
Test connectivity from host and container
Gmail Authentication Errors
Confirm two-factor authentication is enabled
Use an app password, not your account password
Ensure sender email matches the app password owner
Email Delivery Issues
Check spam folder
Verify recipient address
Test with a different recipient
Security Considerations
All LLM processing runs locally
No prompts or emails are sent to external services
Gmail credentials are stored only in memory
App passwords are used instead of account passwords
Future Improvements
Multi-user support
Scheduled email delivery
Report history storage
Support for additional email providers
Monitoring and evaluation dashboard
License
This project may be released under the MIT License.
Add a LICENSE file before publishing publicly.