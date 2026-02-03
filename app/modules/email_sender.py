import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

# Get config from environment directly
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))


def send_email(
    from_email: str,
    app_password: str,
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
):
    """Send email via Gmail SMTP with detailed logging."""
    
    print("=" * 60)
    print(" EMAIL SENDING STARTED")
    print("=" * 60)
    print(f"From: {from_email}")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"SMTP Host: {SMTP_HOST}")
    print(f"SMTP Port: {SMTP_PORT}")
    print(f"App Password Length: {len(app_password)}")
    print("=" * 60)
    
    if text_body is None:
        text_body = "Your client does not support HTML. Please view this email in an HTML-capable client."

    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    part1 = MIMEText(text_body, "plain")
    part2 = MIMEText(html_body, "html")

    msg.attach(part1)
    msg.attach(part2)

    # Create SSL context
    context = ssl.create_default_context()
    
    try:
        print("Step 1: Connecting to SMTP server...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            print(" Connected to SMTP server")
            
            print("Step 2: Starting TLS...")
            server.starttls(context=context)
            print(" TLS started")
            
            print("Step 3: Logging in...")
            server.login(from_email, app_password)
            print(" Login successful")
            
            print("Step 4: Sending message...")
            server.sendmail(from_email, [to_email], msg.as_string())
            print(" Message sent successfully!")
        
        print("=" * 60)
        print(" EMAIL SENT SUCCESSFULLY")
        print("=" * 60)
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f" Authentication Error: {e}")
        raise Exception(f"Authentication failed: {e}")
    
    except smtplib.SMTPException as e:
        print(f" SMTP Error: {e}")
        raise Exception(f"SMTP error: {e}")
    
    except Exception as e:
        print(f" Unexpected Error: {e}")
        raise Exception(f"Failed to send email: {e}")
