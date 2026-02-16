import streamlit as st
from datetime import date
import time

# Import refactored cloud-ready modules
from modules import credential_storage, preferences, report_generator, email_sender
from modules import prompt_parser

st.set_page_config(
    page_title="Email Automation System  v2 - TEST",
    layout="centered",
    initial_sidebar_state="expanded",
)


def apply_custom_css():
    """Apply custom styling."""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #7f8c8d;
            margin-bottom: 2rem;
        }
        .success-box {
            padding: 1rem;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            color: #155724;
            margin: 1rem 0;
        }
        .error-box {
            padding: 1rem;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            color: #721c24;
            margin: 1rem 0;
        }
        .info-box {
            padding: 1rem;
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 8px;
            color: #0c5460;
            margin: 1rem 0;
        }
        
        /* Refined email section */
        .refined-section {
            border: 2px solid #3498db;
            border-radius: 12px;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            margin: 20px 0;
        }
        
        .refined-header {
            font-size: 1rem;
            font-weight: 600;
            color: white;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* Make selectbox non-editable - disable input field */
        div[data-baseweb="select"] input {
            pointer-events: none !important;
            cursor: pointer !important;
            caret-color: transparent !important;
        }
        
        /* Make the entire selectbox clickable */
        div[data-baseweb="select"] {
            cursor: pointer !important;
        }
        
        div[data-baseweb="select"] > div {
            cursor: pointer !important;
        }
        
        /* Style dropdown options */
        div[data-baseweb="popover"] li {
            cursor: pointer !important;
        }
        
        /* Additional selectbox styling */
        .stSelectbox > div > div {
            cursor: pointer !important;
        }
        
        /* Dropdown arrow animation */
        div[data-baseweb="select"] svg {
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            transform-origin: center;
        }
        
        div[data-baseweb="select"][aria-expanded="true"] svg {
            transform: rotate(180deg);
        }
        
        div[data-baseweb="select"][aria-expanded="false"] svg {
            transform: rotate(0deg);
        }
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state for user management."""
    if "current_user_email" not in st.session_state:
        st.session_state["current_user_email"] = None
    if "is_authenticated" not in st.session_state:
        st.session_state["is_authenticated"] = False
    if "form_cleared" not in st.session_state:
        st.session_state["form_cleared"] = False
    if "refined_email_html" not in st.session_state:
        st.session_state["refined_email_html"] = None
    if "show_refined" not in st.session_state:
        st.session_state["show_refined"] = False


def sidebar_credentials():
    """Handle Gmail credentials and user preferences in sidebar."""
    st.sidebar.title("Configuration")
    
    # Check authentication status
    current_user = st.session_state.get("current_user_email")
    
    # Gmail Auth Section
    with st.sidebar.expander("Gmail Credentials", expanded=not current_user):
        st.markdown("**Required for sending emails**")
        
        if current_user:
            st.success(f"**Logged in as:**\n\n`{current_user}`")
            
            # Logout
            if st.button("Logout", use_container_width=True, type="primary"):
                # Clear session state
                st.session_state["current_user_email"] = None
                st.session_state["is_authenticated"] = False
                
                st.success("Logged out successfully!")
                time.sleep(1)
                st.rerun()
        
        else:
            st.info("Please enter your Gmail credentials to send emails")
            
            # Email input
            email = st.text_input(
                "Gmail address",
                placeholder="your.email@gmail.com",
                key="gmail_input",
            )
            
            # App password input
            col_label, col_help = st.columns([0.85, 0.15])

            with col_label:
                st.markdown("**App password**")
            with col_help:
                st.markdown("", help="Generate at: https://myaccount.google.com/apppasswords")

            app_password = st.text_input(
                "App password",
                type="password",
                placeholder="16-character app password",
                key="app_password_input",
                label_visibility="collapsed"
            )
            
            # Login
            if st.button("Login", use_container_width=True, type="primary"):
                if email and app_password:
                    with st.spinner("Validating credentials..."):
                        # Test SMTP connection
                        try:
                            import smtplib
                            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                            server.login(email, app_password)
                            server.quit()
                            
                            # Save to Supabase
                            if credential_storage.save_credentials(email, email, app_password):
                                st.session_state["current_user_email"] = email
                                st.session_state["is_authenticated"] = True
                                st.success("Logged in successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to save credentials")
                        
                        except smtplib.SMTPAuthenticationError:
                            st.error("Authentication failed. Invalid email or app password.")
                            st.info("**How to fix:**\n"
                                   "1. Go to: https://myaccount.google.com/apppasswords\n"
                                   "2. Enable 2-Step Verification\n"
                                   "3. Generate a new App Password\n"
                                   "4. Copy the 16-character code and try again")
                        except Exception as e:
                            st.error(f"Connection failed: {e}")
                else:
                    st.error("Please fill both fields")
    
    # Only show Preferences if logged in
    if current_user:
        # Load preferences from Supabase
        user_prefs = preferences.load_preferences(current_user)
        
        # Preferences Section
        with st.sidebar.expander("Preferences", expanded=False):
            # Sender Name
            sender_name = st.text_input(
                "Sender name",
                value=user_prefs.get("sender_name", ""),
                placeholder="Your name",
                key="sender_name",
            )
            
            # Default Recipient
            st.markdown("**Default recipient email**", help="Auto-fills the recipient field")
            default_recipient = st.text_input(
                "Default recipient email",
                value=user_prefs.get("default_recipient", ""),
                placeholder="manager@company.com",
                key="default_recipient",
                label_visibility="collapsed"
            )
            
            # Default Subject
            st.markdown("**Default subject**", help="Auto-fills the subject field")
            default_subject = st.text_input(
                "Default subject",
                value=user_prefs.get("default_subject", ""),
                placeholder="Daily Task Report",
                key="default_subject",
                label_visibility="collapsed"
            )
            
            # CC/BCC
            cc_emails = st.text_input(
                "CC emails (comma-separated)",
                value=user_prefs.get("cc_emails", ""),
                placeholder="cc1@example.com, cc2@example.com",
                key="cc_emails",
            )
            
            bcc_emails = st.text_input(
                "BCC emails (comma-separated)",
                value=user_prefs.get("bcc_emails", ""),
                placeholder="bcc1@example.com",
                key="bcc_emails",
            )
            
            # Save Preferences Button
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Save", use_container_width=True):
                    prefs_to_save = {
                        "email_tone": st.session_state.get("email_tone", "formal"),
                        "sender_name": sender_name,
                        "cc_emails": cc_emails,
                        "bcc_emails": bcc_emails,
                        "subject_prefix": st.session_state.get("subject_prefix", ""),
                        "default_recipient": default_recipient,
                        "default_subject": default_subject,
                    }
                    
                    if preferences.save_preferences(current_user, prefs_to_save):
                        st.success("Preferences saved!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to save preferences")
            
            with col2:
                if st.button("Clear", use_container_width=True):
                    if preferences.clear_preferences(current_user):
                        st.success("Preferences cleared")
                        time.sleep(1)
                        st.rerun()
        
        # System Info
        with st.sidebar.expander("System Info", expanded=False):
            st.markdown("""
            **Model:** Groq Llama 3.1 8B  
            **Database:** Supabase PostgreSQL  
            **SMTP:** Gmail (Port 465 SSL)
            """)


def extract_manager_name_from_email(email: str) -> str:
    """Try to extract first name from email address."""
    try:
        local_part = email.split("@")[0]
        if "." in local_part:
            first = local_part.split(".")[0]
            return first.capitalize()
        elif "_" in local_part:
            first = local_part.split("_")[0]
            return first.capitalize()
        else:
            return local_part.capitalize()
    except:
        return "Manager"


def regenerate_refined_email(current_user, creds, user_prefs, stored_recipient, stored_subject, stored_prompt):
    """Regenerate refined email from stored prompt."""
    # Clear current refined state
    st.session_state["show_refined"] = False
    st.session_state["refined_email_html"] = None
    
    with st.spinner("Re-refining with AI..."):
        tasks = prompt_parser.extract_tasks(stored_prompt)
        
        if not tasks:
            st.error("Could not extract any tasks.")
            st.stop()
        
        tone = st.session_state.get("email_tone", "formal")

        sender_name = user_prefs.get("sender_name", "")

        if not sender_name:  # Fallback if empty
            sender_name = "Team Member"

        manager_name = extract_manager_name_from_email(stored_recipient)
        
        report = report_generator.generate_email_report(
            tasks=tasks,
            manager_name=manager_name,
            tone=tone,
            sender_name=sender_name,
        )
        
        if stored_subject and stored_subject.strip():
            final_subject = stored_subject.strip()
        else:
            final_subject = report.subject
        
        # Store new refined email
        st.session_state["refined_email_html"] = report.body_html
        st.session_state["refined_subject"] = final_subject
        st.session_state["refined_recipient"] = stored_recipient
        st.session_state["show_refined"] = True
    
    st.rerun()


def html_to_plain_text(html_content: str) -> str:
    """Convert HTML email to editable plain text format."""
    import re
    
    # Remove HTML tags but preserve structure
    text = html_content
    
    # Remove style tags and their content
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    
    # Remove script tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    
    # Replace <br> with newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    
    # Replace list items with bullets
    text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    
    # Replace paragraph breaks
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<p[^>]*>', '', text, flags=re.IGNORECASE)
    
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text


def plain_text_to_html(plain_text: str, sender_name: str = "Task Automation System") -> str:
    """Convert plain text back to HTML email format."""
    lines = plain_text.split('\n')
    html_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Convert bullet points to list items
        if line.startswith('•'):
            html_lines.append(f"<li>{line[1:].strip()}</li>")
        elif line.startswith('-'):
            html_lines.append(f"<li>{line[1:].strip()}</li>")
        else:
            html_lines.append(f"<p>{line}</p>")
    
    html_body = f"""<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 650px;
            margin: 0 auto;
            padding: 20px;
        }}
        p {{
            margin: 10px 0;
        }}
        ul {{
            background: #f8f9fa;
            padding: 20px 20px 20px 40px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }}
        li {{
            margin-bottom: 10px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    {''.join(html_lines)}
    
    <div class="footer">
        <em>This report was sent via Email Automation System.</em>
    </div>
</body>
</html>"""
    
    return html_body


def clear_form():
    """Clear form inputs using a flag-based approach."""
    st.session_state["form_cleared"] = True
    st.session_state["show_refined"] = False
    st.session_state["refined_email_html"] = None
    if "refined_subject" in st.session_state:
        del st.session_state["refined_subject"]
    if "refined_recipient" in st.session_state:
        del st.session_state["refined_recipient"]
    if "last_prompt" in st.session_state:
        del st.session_state["last_prompt"]
    if "last_subject" in st.session_state:
        del st.session_state["last_subject"]
    if "last_recipient" in st.session_state:
        del st.session_state["last_recipient"]


def main():
    apply_custom_css()
    init_session_state()
    sidebar_credentials()
    
    # Main header
    st.markdown('<h1 class="main-header">Email Automation System v2</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Transform your work log into professional email reports, instantly.</p>',
        unsafe_allow_html=True
    )
    
    # Check if user is logged in
    current_user = st.session_state.get("current_user_email")
    
    if not current_user:
        st.warning("Please login with your Gmail credentials in the sidebar to continue.")
        st.stop()
    
    # Load user credentials and preferences
    creds = credential_storage.load_credentials(current_user)
    user_prefs = preferences.load_preferences(current_user)
    
    if not creds:
        st.error("Failed to load credentials. Please login again.")
        st.session_state["current_user_email"] = None
        st.session_state["is_authenticated"] = False
        st.rerun()
    
    # Instructions
    with st.expander("How to use", expanded=False):
        st.markdown("""
        **Step 1:** Configure Gmail credentials in the sidebar
        
        **Step 2:** Select email tone and template (optional)
        
        **Step 3:** Enter recipient email address
        
        **Step 4:** Enter email subject (or use auto-generated)
        
        **Step 5:** Write your work log:
        - List your completed tasks
        - Use any format: bullets, numbers, or plain text
        
        **Step 6:** Choose an action:
        - **Send**: Send your work log as-is (no AI refinement)
        - **Refine**: Generate AI-polished version (editable before sending)
        - **Refine & Send**: Generate and send immediately
        """)
    
    # Example templates
    example_templates = {
        "Custom": "",
        "Software Developers": """Today's tasks:
- Fixed critical navigation bug in EasyCatering mobile app, took 3 hours
- Implemented new dashboard feature for restaurant analytics
- Attended sprint planning meeting and code review
- Started working on user authentication module""",
        
        "Frontend Developer": """Completed today:
- Created wireframes for new onboarding flow
- Conducted user testing session with 5 participants
- Updated design system documentation
- Reviewed and approved icon set from external designer""",
        
        "Social Media Marketing": """Today I:
- Launched Q1 email campaign to 10k subscribers
- Analyzed social media metrics and prepared report
- Coordinated with design team on new landing page
- Scheduled 3 client demos for next week""",
    }
    
    st.markdown("### Compose Your Email")
    
    # Email Tone and Template selector
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Email tone**", help="Choose the tone for your email")
        
        tone_display = ["Formal", "Neutral", "Friendly"]
        tone_values = ["formal", "neutral", "friendly"]
        
        current_tone = user_prefs.get("email_tone", "formal")
        
        try:
            current_index = tone_values.index(current_tone)
        except ValueError:
            current_index = 0
        
        email_tone_display = st.selectbox(
            "Email tone",
            options=tone_display,
            index=current_index,
            key="email_tone_main",
            label_visibility="collapsed"
        )
        
        email_tone = tone_values[tone_display.index(email_tone_display)]
        st.session_state["email_tone"] = email_tone
    
    with col2:
        st.markdown("**Select template**", help="Choose a pre-made template")
        template_choice = st.selectbox(
            "Select template",
            options=list(example_templates.keys()),
            index=0,
            key="template_selector",
            label_visibility="collapsed"
        )
    
    # Initialize session state for templates
    if "raw_prompt_value" not in st.session_state:
        st.session_state["raw_prompt_value"] = ""
    
    if "last_selected_template" not in st.session_state:
        st.session_state["last_selected_template"] = "Custom"
    
    # Detect template change and load content
    if template_choice != st.session_state["last_selected_template"]:
        st.session_state["last_selected_template"] = template_choice
        
        if template_choice != "Custom":
            # Load the selected template
            st.session_state["raw_prompt_value"] = example_templates[template_choice]
        
        # Force rerun to update the text area immediately
        st.rerun()
    
    # Recipient email field
    st.markdown("**Recipient email**", help="Enter the recipient's email address")
    
    default_recipient = "" if st.session_state.get("form_cleared") else user_prefs.get("default_recipient", "")
    recipient_email = st.text_input(
        "Recipient email",
        value=default_recipient,
        placeholder="manager@company.com",
        key="recipient_email_input",
        label_visibility="collapsed"
    )
    
    # Subject field
    st.markdown("**Subject**", help="Enter email subject (leave blank for auto-generated)")
    default_subject = "" if st.session_state.get("form_cleared") else user_prefs.get("default_subject", "")
    subject_input = st.text_input(
        "Subject",
        value=default_subject,
        placeholder="Daily Task Report (auto-generated if left blank)",
        key="subject_input",
        label_visibility="collapsed"
    )
    
    # Work log field OR Refined email field
    if st.session_state.get("show_refined"):
        # Show refined email editor
        st.markdown('<div class="refined-header">Refined Email</div>', unsafe_allow_html=True)
        
        # Convert HTML to editable plain text
        plain_text = html_to_plain_text(st.session_state["refined_email_html"])
        
        refined_content = st.text_area(
            "Refined email content",
            value=plain_text,
            height=350,
            key="refined_email_editor",
            label_visibility="collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons for refined email
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if st.button("Send Refined Email", type="primary", use_container_width=True):
                send_refined_email_action(current_user, creds, user_prefs, recipient_email, subject_input, refined_content)
        
        with col2:
            if st.button("Refine Again", use_container_width=True):
                stored_prompt = st.session_state.get("last_prompt", "")
                stored_subject = st.session_state.get("last_subject", "")
                stored_recipient = st.session_state.get("last_recipient", "")
                
                if stored_prompt:
                    regenerate_refined_email(current_user, creds, user_prefs, stored_recipient, stored_subject, stored_prompt)
                else:
                    st.error("Cannot refine again - original prompt not found")
        
        with col3:
            if st.button("🔙 Start Over", use_container_width=True):
                clear_form()
                st.rerun()
    
    else:
        # Show normal work log input
        st.markdown("**Your work log**", help="List your completed tasks")
        
        if st.session_state.get("form_cleared"):
            st.session_state["raw_prompt_value"] = ""
            st.session_state["last_selected_template"] = "Custom"
            st.session_state["form_cleared"] = False
        
        # Text area with current value
        raw_prompt = st.text_area(
            "Your work log",
            height=250,
            value=st.session_state["raw_prompt_value"],
            placeholder="Today's tasks:\n- Task 1\n- Task 2\n- Task 3",
            key="raw_prompt_input",
            label_visibility="collapsed"
        )
        
        # Only update session state when user actually types
        if raw_prompt != st.session_state["raw_prompt_value"]:
            st.session_state["raw_prompt_value"] = raw_prompt
            
            # If user manually edits and content differs from selected template, switch to Custom
            if st.session_state["last_selected_template"] != "Custom":
                template_content = example_templates.get(st.session_state["last_selected_template"], "")
                if raw_prompt != template_content:
                    # User modified template content, but don't trigger rerun
                    # Just update the tracking variable
                    st.session_state["last_selected_template"] = "Custom"
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            send_button = st.button(
                "📤 Send",
                use_container_width=True,
                help="Send without AI refinement"
            )
        
        with col2:
            refine_button = st.button(
                "✨ Refine",
                use_container_width=True,
                help="Generate AI-polished version (editable)"
            )
        
        with col3:
            refine_and_send_button = st.button(
                "🚀 Refine & Send",
                type="primary",
                use_container_width=True,
                help="Generate and send immediately"
            )
        
        # Validate inputs
        if send_button or refine_button or refine_and_send_button:
            if not recipient_email or not recipient_email.strip():
                st.error("Please enter a recipient email address.")
                st.stop()
            
            if not raw_prompt.strip():
                st.error("Please enter your work log.")
                st.stop()
            
            # Store inputs for potential re-refinement
            st.session_state["last_prompt"] = raw_prompt
            st.session_state["last_subject"] = subject_input
            st.session_state["last_recipient"] = recipient_email
        
        # Handle actions
        if send_button:
            handle_send(current_user, creds, user_prefs, recipient_email, subject_input, raw_prompt)
        elif refine_button:
            handle_refine(current_user, creds, user_prefs, recipient_email, subject_input, raw_prompt)
        elif refine_and_send_button:
            handle_refine_and_send(current_user, creds, user_prefs, recipient_email, subject_input, raw_prompt)


def handle_send(current_user, creds, user_prefs, recipient_email, subject_input, raw_prompt):
    """Handle 'Send' button - send without AI refinement."""
    
    with st.spinner("Processing your work log..."):
        tasks = prompt_parser.extract_tasks(raw_prompt)
        
        if not tasks:
            st.error("Could not extract any tasks.")
            st.stop()
        
        sender_name = user_prefs.get("sender_name", "Task Automation System")
        cc_emails = user_prefs.get("cc_emails", "")
        bcc_emails = user_prefs.get("bcc_emails", "")
        
        date_str = date.today().strftime("%B %d, %Y")
        
        if subject_input and subject_input.strip():
            subject = subject_input.strip()
        else:
            subject = f"Daily Task Report - {date_str}"
        
        # Create plain email
        task_items = "\n".join(f"<li>{task}</li>" for task in tasks)
        html_body = f"""<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Hello,</p>
    <p>Here is my work log for <strong>{date_str}</strong>:</p>
    <ol>{task_items}</ol>
    <p>Best regards,<br><strong>{sender_name}</strong></p>
    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
    <p style="font-size: 0.9em; color: #666;"><em>Sent via Email Automation System.</em></p>
</body>
</html>"""
    
    st.markdown("---")
    st.markdown("### Sending Email")
    
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Preparing email...")
        progress_bar.progress(25)
        time.sleep(0.3)
        
        status_text.text("Connecting to Gmail...")
        progress_bar.progress(50)
        time.sleep(0.3)
        
        status_text.text("Sending email...")
        progress_bar.progress(75)
        
        email_sender.send_email(
            from_email=creds["email"],
            app_password=creds["app_password"],
            to_email=recipient_email,
            subject=subject,
            html_body=html_body,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails,
        )
        
        progress_bar.progress(100)
        status_text.text("Email sent successfully!")
        
        st.success(f"**Email sent to {recipient_email}!**")
        st.snow()
        
        time.sleep(2)
        clear_form()
        st.rerun()
    
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")


def handle_refine(current_user, creds, user_prefs, recipient_email, subject_input, raw_prompt):
    """Handle 'Refine' button - generate AI-refined editable preview."""
    
    with st.spinner("✨ Refining with AI..."):
        tasks = prompt_parser.extract_tasks(raw_prompt)
        
        if not tasks:
            st.error("Could not extract any tasks.")
            st.stop()
        
        tone = st.session_state.get("email_tone", "formal")

        sender_name = user_prefs.get("sender_name", "")

        if not sender_name:  # Fallback if empty
            sender_name = "Team Member"

        manager_name = extract_manager_name_from_email(recipient_email)
        
        report = report_generator.generate_email_report(
            tasks=tasks,
            manager_name=manager_name,
            tone=tone,
            sender_name=sender_name,
        )
        
        if subject_input and subject_input.strip():
            final_subject = subject_input.strip()
        else:
            final_subject = report.subject
        
        # Store refined email for editing
        st.session_state["refined_email_html"] = report.body_html
        st.session_state["refined_subject"] = final_subject
        st.session_state["refined_recipient"] = recipient_email
        st.session_state["show_refined"] = True
    
    st.rerun()


def handle_refine_and_send(current_user, creds, user_prefs, recipient_email, subject_input, raw_prompt):
    """Handle 'Refine & Send' button - generate and send immediately."""
    
    with st.spinner("✨ Refining with AI..."):
        tasks = prompt_parser.extract_tasks(raw_prompt)
        
        if not tasks:
            st.error("Could not extract any tasks.")
            st.stop()
        
        tone = st.session_state.get("email_tone", "formal")
        
        sender_name = user_prefs.get("sender_name", "")

        if not sender_name:  # Fallback if empty
            sender_name = "Team Member"

        manager_name = extract_manager_name_from_email(recipient_email)
        
        report = report_generator.generate_email_report(
            tasks=tasks,
            manager_name=manager_name,
            tone=tone,
            sender_name=sender_name,
        )
        
        if subject_input and subject_input.strip():
            final_subject = subject_input.strip()
        else:
            final_subject = report.subject
    
    st.markdown("---")
    st.markdown("### Email Preview")
    
    with st.expander("View Email Content", expanded=True):
        st.components.v1.html(report.body_html, height=600, scrolling=True)
    
    st.markdown("### Sending Email...")
    
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Preparing email...")
        progress_bar.progress(25)
        time.sleep(0.3)
        
        status_text.text("Connecting to Gmail...")
        progress_bar.progress(50)
        time.sleep(0.3)
        
        status_text.text("Sending email...")
        progress_bar.progress(75)
        
        email_sender.send_email(
            from_email=creds["email"],
            app_password=creds["app_password"],
            to_email=recipient_email,
            subject=final_subject,
            html_body=report.body_html,
            cc_emails=user_prefs.get("cc_emails", ""),
            bcc_emails=user_prefs.get("bcc_emails", ""),
        )
        
        progress_bar.progress(100)
        status_text.text("Email sent successfully!")
        
        st.success(f"**Email sent to {recipient_email}!**")
        st.balloons()
        
        time.sleep(2)
        clear_form()
        st.rerun()
    
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")


def send_refined_email_action(current_user, creds, user_prefs, recipient_email, subject_input, edited_content):
    """Send the edited refined email."""
    
    if not edited_content.strip():
        st.error("Email content cannot be empty.")
        return
    
    sender_name = user_prefs.get("sender_name", "Task Automation System")
    
    # Convert edited plain text back to HTML
    html_body = plain_text_to_html(edited_content, sender_name)
    
    # Use stored subject or custom subject
    if subject_input and subject_input.strip():
        final_subject = subject_input.strip()
    else:
        final_subject = st.session_state.get("refined_subject", "Daily Task Report")
    
    st.markdown("---")
    st.markdown("### Sending Refined Email...")
    
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Preparing...")
        progress_bar.progress(33)
        time.sleep(0.3)
        
        status_text.text("Sending...")
        progress_bar.progress(66)
        
        email_sender.send_email(
            from_email=creds["email"],
            app_password=creds["app_password"],
            to_email=recipient_email,
            subject=final_subject,
            html_body=html_body,
            cc_emails=user_prefs.get("cc_emails", ""),
            bcc_emails=user_prefs.get("bcc_emails", ""),
        )
        
        progress_bar.progress(100)
        status_text.text("Sent!")
        
        st.success(f"**Email sent to {recipient_email}!**")
        st.balloons()
        
        time.sleep(2)
        clear_form()
        st.rerun()
    
    except Exception as e:
        st.error(f"Failed to send: {str(e)}")


if __name__ == "__main__":
    main()