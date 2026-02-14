import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional


def send_email(
    from_email: str,
    app_password: str,
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str = None,
    cc_emails: str = "",
    bcc_emails: str = "",
):
    """
    Send an email via Gmail SMTP with SSL on port 465 (cloud-compatible).
    
    Args:
        from_email: Sender's Gmail address
        app_password: Gmail app password
        to_email: Recipient's email address
        subject: Email subject
        html_body: HTML version of email body
        text_body: Plain text version (optional)
        cc_emails: Comma-separated CC emails (optional)
        bcc_emails: Comma-separated BCC emails (optional)
    """
    # Create message
    msg = MIMEMultipart("alternative")
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    
    # Add CC if provided
    if cc_emails and cc_emails.strip():
        msg["Cc"] = cc_emails.strip()
    
    # Attach plain text version (fallback)
    if text_body:
        part1 = MIMEText(text_body, "plain")
        msg.attach(part1)
    
    # Attach HTML version
    part2 = MIMEText(html_body, "html")
    msg.attach(part2)
    
    # Parse all recipients (TO + CC + BCC)
    all_recipients = [to_email]
    
    if cc_emails and cc_emails.strip():
        cc_list = [email.strip() for email in cc_emails.split(",") if email.strip()]
        all_recipients.extend(cc_list)
    
    if bcc_emails and bcc_emails.strip():
        bcc_list = [email.strip() for email in bcc_emails.split(",") if email.strip()]
        all_recipients.extend(bcc_list)
    
    # Use SMTP_SSL on port 465 for cloud compatibility
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(from_email, app_password)
        server.sendmail(from_email, all_recipients, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {len(all_recipients)} recipient(s)")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise Exception(f"Failed to send email: {str(e)}")
