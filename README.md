Email Task Report Automation System
A production-ready web application that converts daily work logs into professional email reports and sends them automatically via Gmail.
The system runs a local LLM using Ollama, provides a Streamlit-based UI, and is fully containerized with Docker.
This tool is designed to eliminate repetitive email formatting while keeping full control over data and credentials.
What This Does
You enter a daily work log in plain English, including the recipient’s email address. The application:
Extracts the recipient email and task list
Structures tasks into a professional report
Generates an HTML email using a local LLM
Sends the email via Gmail SMTP
Shows a preview and delivery confirmation
All LLM processing runs locally. No external AI APIs are used.
Key Features
Natural language task input (free text or bullet points)
Automatic recipient and task extraction
AI-generated professional HTML emails
Multiple writing tones: formal, neutral, friendly
Gmail SMTP integration using app passwords
Deterministic fallback email generation if LLM fails
Fully Dockerized for consistent deployment
Local-first design with no data leaving the machine
Tech Stack
Frontend
Streamlit
Custom CSS
Backend
Python 3.11
LangChain
Regex-based parsing
LLM Runtime
Ollama
Llama 3.1 (8B)
Email
smtplib
email.mime
Gmail SMTP (TLS)
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
│   └── generate_dataset.py
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
1. Clone the Repository
git clone https://github.com/your-username/email-automation-system.git
cd "Email Automation System"
2. Install and Run Ollama
ollama pull llama3.1:8b
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
Verify:
curl http://localhost:11434/api/tags
3. Run the Application with Docker
docker-compose build
docker-compose up -d
docker logs -f task-report-automation
The app will be available at:
http://localhost:8501
Gmail App Password Setup
Gmail requires app passwords when 2FA is enabled.
Visit https://myaccount.google.com/apppasswords
Create a new app password (Other → custom name)
Copy the 16-character password (no spaces)
Using the Application
Configure Email Credentials
Enter your Gmail address
Enter the Gmail app password
Credentials are stored only in memory (session state)
Enter a Work Log
Example:
Send to: manager@company.com

Today's tasks:
- Fixed critical navigation bug
- Implemented analytics dashboard
- Attended sprint planning
- Started authentication module
Generate and Send
Preview Only: Generate email without sending
Generate & Send: Generate and send via Gmail
The app displays:
Recipient
Subject
Task count
Generation method (LLM or fallback)
HTML preview
Core Modules
prompt_parser.py
Extracts recipient email
Detects tasks using bullets, numbering, and headers
Outputs a clean task list
report_generator.py
Connects to Ollama
Builds structured LLM prompts
Cleans and validates HTML output
Falls back to template-based generation if needed
email_sender.py
Sends multipart (text + HTML) emails via Gmail SMTP
Uses TLS and app password authentication
email_auth.py
Stores credentials in Streamlit session state
No disk persistence
Configuration
Environment variables (via docker-compose.yml):
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
LLM Not Connecting
Ensure ollama serve is running
Verify OLLAMA_HOST is reachable from Docker
Test with curl from host and container
Gmail Authentication Errors
Confirm 2FA is enabled
Use app password, not account password
Ensure sender email matches the app password owner
Emails Not Received
Check spam folder
Verify recipient address
Test with a different recipient
Security Notes
LLM runs entirely locally
No prompts or content sent to external services
Gmail credentials stored only in memory
App passwords are used instead of account passwords
Possible Extensions
Multi-user support
Scheduled daily reports
Report history storage
Additional email providers
Monitoring and evaluation dashboard
License
This project can be released under the MIT License.
Add a LICENSE file before publishing.