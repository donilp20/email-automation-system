Email Task Report Automation System – Technical Documentation
1. Overview
Email Task Report Automation System is a local-first automation tool that converts daily work logs into structured, professional email reports and sends them automatically via Gmail.
The application uses a locally running large language model through Ollama, a Streamlit-based web interface, and Docker for reproducible deployment. All AI processing runs locally, with no reliance on external LLM APIs.
2. System Workflow
User enters a daily work log in natural language
Recipient email and task list are automatically extracted
Tasks are structured into a professional report
A local LLM generates an HTML email
Email is sent via Gmail SMTP
User receives a preview and confirmation
3. Key Features
Natural language work log input
Automatic recipient and task extraction
HTML email generation using a local LLM
Multiple tone options: formal, neutral, friendly
Gmail SMTP integration using app passwords
Fallback template-based email generation
Fully Dockerized deployment
No external AI or third-party data sharing
4. Technology Stack
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
Email Infrastructure
smtplib
email.mime
Gmail SMTP with TLS
Deployment
Docker
docker-compose
5. Project Structure
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
6. Prerequisites
macOS
Docker Desktop
Ollama installed locally
Gmail account with:
Two-factor authentication enabled
App password generated
7. Setup Instructions
7.1 Clone the Repository
git clone https://github.com/your-username/email-automation-system.git
cd "Email Automation System"
7.2 Install and Run Ollama
ollama pull llama3.1:8b
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
Verify Ollama is running:
curl http://localhost:11434/api/tags
7.3 Build and Run with Docker
docker-compose build
docker-compose up -d
docker logs -f task-report-automation
The application will be available at:
http://localhost:8501
8. Gmail App Password Setup
Gmail requires app passwords when two-factor authentication is enabled.
Visit: https://myaccount.google.com/apppasswords
Create a new app password with a custom name
Copy the 16-character password (no spaces)
9. Using the Application
9.1 Configure Email Credentials
Enter your Gmail address
Enter the Gmail app password
Credentials are stored only in Streamlit session state
9.2 Enter a Work Log
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
9.3 Generate and Send
Preview Only: Generates the email without sending
Generate & Send: Generates and sends the email via Gmail
Displayed information:
Recipient
Subject
Task count
Generation method (LLM or fallback)
HTML preview
10. Core Modules
prompt_parser.py
Extracts recipient email from input text
Identifies task lines using bullets, numbering, and headers
Outputs a clean list of tasks
report_generator.py
Connects to Ollama using environment configuration
Builds structured prompts for the LLM
Cleans and validates generated HTML
Falls back to a deterministic template when needed
email_sender.py
Sends multipart (text and HTML) emails
Uses Gmail SMTP with TLS
Handles authentication and delivery logging
email_auth.py
Stores credentials in Streamlit session state
Does not persist sensitive data to disk
11. Configuration
Environment variables provided via docker-compose.yml:
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1:8b
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
12. Security Considerations
All LLM processing runs locally
No prompts or email content are sent externally
Gmail credentials are stored only in memory
App passwords are used instead of account passwords
13. Future Improvements
Multi-user support
Scheduled email delivery
Report history storage
Support for additional email providers
Monitoring and evaluation dashboard
14. License
This project may be released under the MIT License.
Add a LICENSE file before publishing publicly.