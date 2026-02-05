# 📧 Email Task Report Automation System

> **Transform your daily work log into professional email reports with AI-powered generation and automated Gmail delivery.**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-FF4B4B.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![LLM](https://img.shields.io/badge/LLM-Llama%203.1%208B-orange.svg)](https://ollama.ai/)

---

## 🎯 Overview

**Email Task Report Automation System** is a production-ready web application designed to streamline your daily work reporting. Simply paste your work log in natural language, and the system automatically:

- **Extracts** recipient email addresses
- **Structures** your tasks intelligently
- **Generates** professional HTML emails using a local LLM (Llama 3.1 8B)
- **Sends** reports via Gmail SMTP with secure authentication
- **Previews** your email before sending

**Key Differentiator:** All AI processing runs **locally via Ollama** — no external API calls, no data leaves your machine, and no subscription costs.

---

## ✨ Features

### 🤖 AI-Powered Generation
- **Local LLM Integration**: Llama 3.1 8B running via Ollama for privacy-first email generation
- **Multiple Tone Options**: Choose between formal, neutral, or friendly communication styles
- **Smart Fallback**: Template-based HTML generation when LLM is unavailable

### 📝 Intelligent Parsing
- **Natural Language Input**: Paste tasks as bullets, numbered lists, or plain paragraphs
- **Automatic Email Detection**: Extracts recipient addresses using regex and heuristics
- **Context-Aware Structuring**: Identifies task headers, completions, and in-progress items

### 🔒 Secure Email Delivery
- **Gmail SMTP**: Industry-standard TLS encryption (port 587)
- **App Password Authentication**: Secure credential management without exposing main password
- **Session-Only Storage**: Credentials stored in memory, never written to disk

### 🐳 Production-Ready Deployment
- **Fully Dockerized**: Consistent environment across all platforms
- **Docker Compose**: One-command orchestration of app and dependencies
- **Graceful Degradation**: Automatic fallback when services are unavailable

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                         │
│              (User Input + Email Preview)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   Prompt Parser        │
         │  (Extract Email +      │
         │   Structure Tasks)     │
         └────────┬───────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │   Report Generator          │
    │   ┌─────────────────────┐  │
    │   │  Ollama LLM         │  │
    │   │  (Llama 3.1 8B)     │  │
    │   └─────────────────────┘  │
    │          ↓ (on fail)       │
    │   ┌─────────────────────┐  │
    │   │  Fallback Template  │  │
    │   └─────────────────────┘  │
    └─────────┬───────────────────┘
              │
              ▼
    ┌────────────────────────┐
    │   Email Sender         │
    │   (Gmail SMTP/TLS)     │
    └────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Interactive web UI with custom CSS |
| **Backend** | Python 3.11 | Core application logic |
| **AI/ML** | Ollama + Llama 3.1 8B | Local LLM for email generation |
| **Orchestration** | LangChain | LLM integration and prompt management |
| **Email** | smtplib + MIME | Gmail SMTP with TLS encryption |
| **Parsing** | Regex + Heuristics | Email extraction and task structuring |
| **Containerization** | Docker + Docker Compose | Isolated, reproducible environment |

---

## 📂 Project Structure

```
Email-Automation-System/
│
├── app/
│   ├── app.py                      # Main Streamlit application
│   ├── config.py                   # Environment configuration (Ollama, SMTP)
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── email_auth.py           # Gmail credential management
│   │   ├── email_sender.py         # SMTP email delivery
│   │   ├── prompt_parser.py        # NLP-based task extraction
│   │   └── report_generator.py     # LLM + fallback email generation
│   │
│   ├── data/
│   │   ├── evaluation_results.json # Parser performance metrics
│   │   └── synthetic_dataset.csv   # Training/testing data
│   │
│   └── prompts/                    # (Optional) Prompt engineering templates
│
├── scripts/
│   ├── evaluate_parser.py          # Parser accuracy evaluation
│   └── generate_dataset.py         # Synthetic data generation
│
├── Dockerfile                      # App container definition
├── docker-compose.yml              # Multi-service orchestration
├── requirements.txt                # Python dependencies
│
├── .dockerignore
├── .gitignore
└── README.md                       # This file
```

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:

- **macOS** (or Linux/Windows with Docker)
- **Docker Desktop** installed and running
- **Ollama** installed ([Download here](https://ollama.ai/))
- **Gmail account** with:
  - Two-Factor Authentication (2FA) enabled
  - App password generated ([Instructions](#gmail-setup))

---

### Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/email-automation-system.git
cd email-automation-system
```

#### 2️⃣ Install and Configure Ollama

```bash
# Pull the Llama 3.1 8B model
ollama pull llama3.1:8b

# Configure Ollama to accept Docker connections
export OLLAMA_HOST=0.0.0.0:11434

# Start Ollama server (keep this terminal running)
ollama serve
```

**Verify Ollama is Running:**
```bash
curl http://localhost:11434/api/tags
```

Expected output: JSON listing `llama3.1:8b`

#### 3️⃣ Build and Launch the Application

```bash
# Build Docker images
docker-compose build

# Start containers in detached mode
docker-compose up -d

# View logs (optional)
docker logs -f task-report-automation
```

**Success indicator:** You should see:
```
Ollama connected: llama3.1:8b at http://host.docker.internal:11434
```

#### 4️⃣ Access the Application

Open your browser and navigate to:
```
http://localhost:8501
```

---

## 🔐 Gmail Setup

### Creating an App Password

Since Gmail blocks direct password authentication on 2FA-enabled accounts, you must generate an app password:

1. Visit [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Sign in and verify 2FA
3. Under **"Select app"**, choose **"Other (Custom name)"**
4. Enter: `Task Report Automation`
5. Click **"Generate"**
6. Copy the **16-character password** (no spaces needed in the app)

⚠️ **Security Note:** Store this password securely. It grants full email sending access.

---

## 📖 Usage Guide

### Step 1: Configure Gmail Credentials

In the **Streamlit sidebar**:
1. Enter your Gmail address (e.g., `your.email@gmail.com`)
2. Paste your 16-character app password
3. Click **"Save"**

✅ The sidebar will confirm: *"Gmail credentials configured"*

### Step 2: Compose Your Work Log

**Option A:** Use a template
- Select from the **"Select Template"** dropdown
- Pre-filled templates demonstrate proper formatting

**Option B:** Write your own
```
Send to: manager@techcorp.com

Today's tasks:
- Fixed critical navigation bug in EasyCatering mobile app (3 hours)
- Implemented restaurant analytics dashboard feature
- Attended sprint planning meeting and code review session
- Started user authentication module development
```

**Formatting Tips:**
- **Recipient**: Include `Send to: email@example.com` on its own line
- **Tasks**: Use bullets (`-`), asterisks (`*`), or numbers (`1.`)
- **Headers**: Optional headers like "Today's tasks:", "Completed:", "In progress:"

### Step 3: Generate and Send

**Two options:**

1. **Generate & Send** (recommended)
   - Parses input → Generates email → Sends immediately → Shows confirmation

2. **Preview Only**
   - Generates email but **does not send**
   - Useful for reviewing format and content

### Step 4: Review Output

The app displays:
- ✉️ **To:** Recipient email
- 📋 **Subject:** "Daily Task Report - [Date]"
- 🔢 **Tasks Detected:** Count of parsed tasks
- 🤖 **Generation Method:** LLM or Fallback
- 👁️ **HTML Preview:** Full email rendering

If satisfied, emails send instantly via Gmail SMTP.

---

## 🧪 Example Scenarios

### Scenario 1: Standard Daily Update

**Input:**
```
Send to: sarah.manager@company.com

Completed today:
- Resolved API authentication bug (Issue #234)
- Code review for frontend team (3 PRs)
- Updated documentation for new endpoints

In progress:
- Database migration planning
```

**Output:** Professional HTML email with structured sections, proper greeting, and formal tone.

---

### Scenario 2: Multi-Project Report

**Input:**
```
To: team-lead@startup.io

Project Alpha:
- Deployed v2.1.0 to staging environment
- Fixed payment gateway integration

Project Beta:
- Completed user interview analysis
- Started wireframe designs for mobile app
```

**Output:** Categorized email with project headers, maintaining context and clarity.

---

## 🔧 Configuration

### Environment Variables

The application is configured via environment variables in `docker-compose.yml`:

```yaml
environment:
  - OLLAMA_HOST=http://host.docker.internal:11434
  - OLLAMA_MODEL=llama3.1:8b
  - SMTP_HOST=smtp.gmail.com
  - SMTP_PORT=587
```

**Customization:**
- **OLLAMA_MODEL**: Change to any Ollama-supported model
- **SMTP_HOST/PORT**: Use different email providers (e.g., Outlook: `smtp-mail.outlook.com:587`)

### Running Without Docker (Local Development)

If you prefer running directly on your host machine:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OLLAMA_HOST=http://127.0.0.1:11434
export OLLAMA_MODEL=llama3.1:8b

# Ensure Ollama is running
ollama serve  # In separate terminal

# Launch app
streamlit run app/app.py
```

---

## 🧩 Core Modules

### 1. `prompt_parser.py`

**Purpose:** Extracts structured data from natural language input.

**Key Functions:**
- `extract_recipient_email(text)` → Finds first valid email address
- `extract_tasks(text)` → Identifies bullet points, numbered items, and task headers

**Logic:**
- Regex patterns for email validation
- Heuristic detection of task markers (`-`, `*`, `1.`)
- Header recognition ("Today's tasks", "Completed", etc.)

---

### 2. `report_generator.py`

**Purpose:** Generates professional HTML emails using LLM or fallback template.

**Workflow:**
1. Connect to Ollama via LangChain
2. Construct prompt with:
   - Manager name
   - Current date
   - Sender name
   - Selected tone (formal/neutral/friendly)
   - Task list
3. Invoke LLM (Llama 3.1 8B)
4. Clean output:
   - Remove code fences (` ```html `)
   - Validate HTML structure
5. On failure: Use deterministic HTML template

**Fallback Template:**
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .task { margin: 10px 0; }
    </style>
</head>
<body>
    <h2>Daily Task Report</h2>
    <p>Dear [Manager],</p>
    <ul>
        <!-- Task list -->
    </ul>
    <p>Best regards,<br>[Your Name]</p>
</body>
</html>
```

---

### 3. `email_sender.py`

**Purpose:** Sends emails via Gmail SMTP with TLS encryption.

**Process:**
1. Connect to `smtp.gmail.com:587`
2. Start TLS encryption
3. Authenticate using Gmail + app password
4. Build MIME multipart message:
   - Plain text version (for accessibility)
   - HTML version (for styling)
5. Send and log results

**Error Handling:**
- Catches SMTP authentication errors
- Logs connection issues
- Provides user-friendly error messages

---

### 4. `email_auth.py`

**Purpose:** Manages Gmail credentials securely in session state.

**Features:**
- Stores credentials in Streamlit's `session_state` (memory only)
- Hashes app password for integrity verification
- **Never writes to disk**
- Credentials persist only during active session

---

## 🐛 Troubleshooting

### Issue: "Could not connect to Ollama"

**Symptoms:** Logs show LLM connection failure, app uses fallback generation.

**Solutions:**
1. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```
2. Check `OLLAMA_HOST` environment variable:
   ```bash
   export OLLAMA_HOST=0.0.0.0:11434
   ollama serve
   ```
3. Test Docker container can reach host:
   ```bash
   docker exec -it task-report-automation curl http://host.docker.internal:11434/api/tags
   ```

---

### Issue: "SMTP Authentication Failed (535)"

**Symptoms:** Email sending fails with authentication error.

**Solutions:**
1. Confirm 2FA is enabled on Gmail account
2. Verify you're using **app password**, not regular password
3. Enter app password **without spaces**
4. Ensure "From" email matches account that generated app password

---

### Issue: Emails Not Arriving

**Solutions:**
1. Check recipient's **spam folder**
2. Verify recipient email address is correct
3. Test with different recipient (e.g., your own secondary email)
4. Review Gmail's "Sent" folder to confirm delivery

---

### Issue: Docker Container Fails to Start

**Solutions:**
1. Check Docker Desktop is running
2. Verify port 8501 is not in use:
   ```bash
   lsof -i :8501
   ```
3. Review logs:
   ```bash
   docker logs task-report-automation
   ```
4. Rebuild containers:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

---

## 🔒 Security Considerations

### ✅ Privacy-First Design

- **Local LLM**: All AI processing happens on your machine via Ollama
- **No External APIs**: Zero data transmission to third-party AI providers
- **In-Memory Credentials**: Gmail passwords stored only in session state
- **No Disk Persistence**: Credentials never written to configuration files

### ✅ Email Security

- **TLS Encryption**: All SMTP connections use port 587 with StartTLS
- **App Passwords**: Gmail authentication isolated from main account password
- **Credential Isolation**: Each user session maintains separate credentials

### ⚠️ Best Practices

1. **Keep repository private** if it contains test logs or real email addresses
2. **Rotate app passwords** periodically (every 90 days recommended)
3. **Review Docker logs** for sensitive information before sharing
4. **Use `.gitignore`** to exclude `.env` files and credential stores

---

## 🚀 Extending the System

### Suggested Enhancements

#### 1. Multi-User Support
- Add user authentication (e.g., OAuth, JWT)
- Store credentials in encrypted database
- Implement role-based access control

#### 2. Scheduling and Automation
- Integrate with cron jobs or Celery for scheduled sends
- Add recurring report templates (daily, weekly, monthly)
- Implement reminder notifications

#### 3. Analytics Dashboard
- Track sent reports (count, timestamps, recipients)
- Monitor LLM vs. fallback generation rates
- Display parser accuracy metrics

#### 4. Multi-Provider Email Support
- Add Outlook/Office 365 SMTP
- Support custom SMTP servers
- Implement email provider auto-detection

#### 5. Advanced Parser Evaluation
- Build synthetic dataset generator
- Implement parser accuracy benchmarks
- Add support for multi-language task descriptions

---

## 🧪 Testing

### Parser Evaluation

Evaluate prompt parsing accuracy:

```bash
python scripts/evaluate_parser.py
```

**Output:** JSON report with precision, recall, and F1 scores for email extraction and task detection.

### Synthetic Dataset Generation

Generate test data for parser training:

```bash
python scripts/generate_dataset.py --samples 100
```

**Output:** `app/data/synthetic_dataset.csv` with diverse task report examples.

---

## 📊 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **LLM Response Time** | 2-5 seconds | Depends on hardware (CPU/GPU) |
| **Fallback Generation** | <100ms | Template-based, instant |
| **Email Delivery** | 1-3 seconds | Gmail SMTP latency |
| **Parser Accuracy** | 95%+ | Email extraction on clean input |
| **Docker Image Size** | ~1.2GB | Includes Python 3.11 + dependencies |

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. **Fork** the repository
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes:
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push** to your branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guidelines for Python code
- Add unit tests for new features
- Update documentation (README, docstrings)
- Ensure Docker build succeeds before submitting PR

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Technologies

- **[Ollama](https://ollama.ai/)** - Local LLM runtime
- **[Llama 3.1 8B](https://ai.meta.com/llama/)** - Meta's open-source language model
- **[Streamlit](https://streamlit.io/)** - Python web framework
- **[LangChain](https://langchain.com/)** - LLM orchestration library
- **[Docker](https://www.docker.com/)** - Containerization platform

### Inspiration

Built to solve the daily pain point of manually formatting work reports for busy developers and professionals.

---

## 📞 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/your-username/email-automation-system/issues)
- **Email:** your.email@example.com
- **LinkedIn:** [Your Profile](https://linkedin.com/in/yourprofile)

---

## 🗓️ Changelog

### v1.0.0 (2026-02-04)
- ✨ Initial release
- 🤖 Local LLM integration via Ollama
- 📧 Gmail SMTP support with app passwords
- 🐳 Full Docker containerization
- 📝 Smart prompt parsing with task extraction
- 🎨 Multiple email tone options
- 🔒 Secure credential management

---

<div align="center">

**Made with ❤️ by [Your Name]**

If this project helped you, consider giving it a ⭐️ on GitHub!

</div>
