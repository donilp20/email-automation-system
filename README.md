Email Task Report Automation System
This project is a production-ready web application that turns your daily work log into a professional email report and sends it automatically via Gmail. It is built with Streamlit, runs an LLM locally via Ollama, and is fully containerized with Docker.

Overview
The goal of this system is simple: you type your work log in natural language, including your manager’s email address, and the app:

Extracts the recipient email.

Parses and structures your tasks.

Uses a local LLM (Llama 3.1 8B via Ollama) to generate a professional HTML email.

Sends the email through Gmail SMTP using an app password.

Shows you a preview and confirmation.

You get consistent, polished daily updates without manually formatting emails.

Features
Natural language input: paste your daily tasks as plain text or bullets.

Smart parsing: extracts recipient email and task list using regex and heuristics.

AI email generation: generates HTML emails using Llama 3.1 8B running locally via Ollama.

Multiple tones: choose formal, neutral, or friendly style.

Gmail SMTP integration: uses app passwords for secure authentication.

Fallback generation: template-based HTML emails if the LLM is unavailable or fails.

Dockerized: consistent Python environment and easy deployment.

Local-first: all LLM calls run on your machine, no external LLM API.

Tech Stack
Frontend / UI

Streamlit (Python)

Custom CSS for styling

Backend / Logic

Python 3.11

LangChain (for LLM orchestration with Ollama)

Regex-based prompt parsing

LLM Runtime

Ollama (local LLM server)

Llama 3.1 8B model

Email Infrastructure

smtplib (standard library)

email.mime (standard library)

Gmail SMTP (smtp.gmail.com, port 587, TLS)

Deployment

Docker

docker-compose

Project Structure
text
Email Automation System/
├── app/
│   ├── app.py                      # Main Streamlit app
│   ├── config.py                   # Configuration (Ollama, SMTP)
│   ├── data/
│   │   ├── evaluation_results.json
│   │   └── synthetic_dataset.csv
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── email_auth.py           # Gmail credential handling
│   │   ├── email_sender.py         # SMTP email sending
│   │   ├── prompt_parser.py        # Extracts email and tasks from text
│   │   └── report_generator.py     # LLM and fallback email generation
│   └── prompts/                    # (Optional) prompt templates
├── scripts/
│   ├── evaluate_parser.py          # Parser evaluation utilities
│   └── generate_dataset.py         # Synthetic dataset generation
├── Dockerfile                      # App container definition
├── docker-compose.yml              # Multi-service setup (app + Ollama host)
├── requirements.txt                # Python dependencies
├── .dockerignore
└── .gitignore
Prerequisites
macOS with Docker Desktop installed and running.

Ollama installed on your Mac.

Gmail account with:

Two-factor authentication (2FA) enabled.

App password created for this app.

Setup
1. Clone the Repository

bash
git clone https://github.com/your-username/email-automation-system.git
cd "Email Automation System"
2. Install and Configure Ollama

If you have not already installed Ollama, install it from the official site, then:

bash
# Pull the Llama 3.1 8B model
ollama pull llama3.1:8b

# Make Ollama listen on all interfaces so Docker can reach it
export OLLAMA_HOST=0.0.0.0:11434

# Start the Ollama server
ollama serve
Keep this terminal window running. You can verify Ollama is up with:

bash
curl http://localhost:11434/api/tags
You should see JSON listing the llama3.1:8b model.

3. Build and Run the Docker Container

In a new terminal window, from the project root:

bash
# Build the app image
docker-compose build

# Start the app container in the background
docker-compose up -d

# Check logs
docker logs -f task-report-automation
You should see a line similar to:

text
Ollama connected: llama3.1:8b at http://host.docker.internal:11434
The app will be available at:

text
http://localhost:8501
Gmail Setup (App Password)
Because Gmail blocks direct username/password SMTP logins on accounts with 2FA, you must use an app password.

Go to: https://myaccount.google.com/apppasswords

Select your account and confirm 2FA.

Under “Select app”, choose “Other (Custom name)” and enter a label such as “Task Report Automation”.

Click “Generate”.

Copy the 16-character app password (no spaces when you use it in the app).

Using the Application
1. Configure Gmail Credentials

In the Streamlit sidebar:

Enter your Gmail address, for example:

your.email@gmail.com

Enter your Gmail app password (the 16-character token).

Click “Save”.

The sidebar will show whether credentials are configured.

Credentials are kept only in Streamlit’s session state (in memory) and not written to disk.

2. Enter Your Work Log

In the main area of the app:

Optionally select a template from the “Load example” dropdown.

Paste or type your work log.

Example:

text
Send to: manager@techcorp.com

Today's tasks:
- Fixed critical navigation bug in EasyCatering mobile app, took 3 hours
- Implemented new dashboard feature for restaurant analytics
- Attended sprint planning meeting and code review
- Started working on user authentication module
The important pieces are:

A line indicating the recipient, such as “Send to: manager@company.com”.

A list or description of tasks.

3. Generate and Send

You have two buttons:

“Generate & Send” – parse tasks, generate email via LLM, send via Gmail.

“Preview Only” – parse tasks and generate email, but do not send.

When you click “Generate & Send”:

The app checks that Gmail credentials are configured.

It parses the prompt to extract:

Recipient email.

Task lines.

It constructs a prompt for Llama 3.1 and requests a full HTML email.

If LLM output is valid HTML, it uses that. If not, it falls back to a template-based HTML email.

It shows:

To: email

Subject

Number of tasks detected

Generation method (LLM or fallback)

An HTML preview of the email.

It sends the email to the recipient via Gmail SMTP.

If sending succeeds, you will see a success message and the form can reset.

Core Modules
prompt_parser.py

Extracts the first email address from the input text.

Detects task lines using:

Bullet markers (-, *).

Numbered lists (1., 2)).

Headers like “Today’s tasks”, “Completed today”, etc.

Returns a flat list of task strings, suitable for feeding into the LLM or fallback generator.

report_generator.py

Connects to Ollama using the model and host defined by environment variables.

Builds a prompt that includes:

Manager name.

Date.

Sender name.

Tone (formal, neutral, friendly).

The list of tasks formatted as bullet points.

Calls the LLM via LangChain’s Ollama integration.

Cleans up LLM output:

Handles cases where the model wraps HTML in code fences (orhtml).

Ensures the result is a valid HTML string containing <html> and <body>.

If anything goes wrong (invalid HTML, exception, timeout), falls back to a deterministic HTML template that still looks professional.

email_sender.py

Uses smtplib and ssl to connect to smtp.gmail.com on port 587.

Starts TLS, logs in with the configured Gmail address and app password.

Builds a multipart message with both plain text and HTML versions.

Sends the email and logs the steps and results.

email_auth.py

Stores Gmail address and app password in Streamlit’s session_state.

Hashes the app password for optional integrity checking.

Does not write credentials to disk.

Environment and Configuration
The app reads its configuration mainly from environment variables, supplied via docker-compose.yml:

text
environment:
  - OLLAMA_HOST=http://host.docker.internal:11434
  - OLLAMA_MODEL=llama3.1:8b
  - SMTP_HOST=smtp.gmail.com
  - SMTP_PORT=587
In Container:

app/config.py uses these environment variables to configure the LLM and SMTP host/port.

On the Host:

Ollama is started with OLLAMA_HOST=0.0.0.0:11434 so that the Docker container can reach it using host.docker.internal:11434.

Running Without Docker (Optional)
If you prefer to run directly on your host without Docker:

Create and activate a virtual environment.

Install requirements:

bash
pip install -r requirements.txt
Ensure Ollama is running:

bash
export OLLAMA_HOST=http://127.0.0.1:11434
ollama serve
Run Streamlit:

bash
streamlit run app/app.py
The rest of the workflow in the browser remains the same.

Troubleshooting
LLM Connection Errors

Symptom: Logs show “Warning: Could not connect to Ollama” and the app always uses fallback generation.

Check:

Is ollama serve running?

Is OLLAMA_HOST set to 0.0.0.0:11434 before starting Ollama when using Docker?

Does curl http://localhost:11434/api/tags work on the host?

Does docker exec -it task-report-automation curl http://host.docker.internal:11434/api/tags work inside the container?

Gmail Authentication Errors

Symptom: SMTP authentication error (e.g., 535).

Check:

2FA is enabled on your Gmail account.

You are using an app password, not your regular Gmail password.

The app password is entered with no spaces.

The “From” address in the app matches the Gmail account that generated the app password.

Emails Not Arriving

Check the recipient’s spam folder.

Verify that the recipient email address is correct.

Try with a simpler test email and a different recipient.

Security Considerations
LLM runs locally; no prompts or content are sent to external AI providers.

Gmail credentials:

Stored only in memory via Streamlit session state.

Not written to disk.

Use app passwords instead of your main Gmail password.

Keep the repository private if it ever contains real addresses, test logs, or configuration files tied to production accounts.

Extending the System
Some possible next steps:

Add user authentication and multi-user profile support.

Allow scheduling (e.g., daily email at a fixed time using a job scheduler).

Store sent reports in a database for history and analytics.

Add support for other email providers (Outlook, custom SMTP).

Add a separate evaluation and monitoring dashboard for parser accuracy and email quality.

License and Attribution
You can license this project under a permissive license such as MIT. Make sure to include a LICENSE file if you plan to share it publicly.

Attributions:

Llama 3.1 8B via Ollama for local LLM capabilities.

Streamlit for the web UI framework.

LangChain for LLM orchestration.