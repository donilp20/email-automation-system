import streamlit as st
from datetime import date
import time

from modules import email_auth, email_sender, prompt_parser, report_generator

import os
APP_TITLE = os.getenv("APP_TITLE", "Email Automation System")

st.set_page_config(
    page_title=APP_TITLE,
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
        
        /* Selectbox cursor */
        div[data-baseweb="select"] {
            cursor: pointer !important;
        }
        
        div[data-baseweb="select"] > div {
            cursor: pointer !important;
        }
        
        /* Dropdown items cursor */
        div[data-baseweb="popover"] li {
            cursor: pointer !important;
        }
        
        /* Select input cursor */
        .stSelectbox > div > div {
            cursor: pointer !important;
        }
        
        /* Arrow rotation animation - Match expander style */
        div[data-baseweb="select"] svg {
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            transform-origin: center;
        }
        
        /* Rotate arrow when dropdown is open - smooth like expander */
        div[data-baseweb="select"][aria-expanded="true"] svg {
            transform: rotate(180deg);
        }
        
        /* Keep arrow normal when closed */
        div[data-baseweb="select"][aria-expanded="false"] svg {
            transform: rotate(0deg);
        }
    </style>
    """, unsafe_allow_html=True)


def sidebar_credentials():
    """Handle Gmail credentials and user preferences in sidebar."""
    st.sidebar.title("Configuration")
    
    # Auto-load credentials
    email_auth.load_saved_credentials()
    
    # Gmail Auth Section
    with st.sidebar.expander("Gmail Credentials", expanded=True):
        st.markdown("**Required for sending emails**")
        
        # Check if credentials are loaded
        from_email, _ = email_auth.get_credentials()
        saved_on_disk = email_auth.credentials_are_saved_on_disk()
        
        if from_email:
            st.success(f"**Logged in as:**\n\n`{from_email}`")
            
            # Logout
            if st.button("Logout", use_container_width=True, type="primary"):
                # ONLY clear credentials, NOT preferences
                email_auth.clear_credentials(delete_from_disk=True)
                
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
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
            app_password = st.text_input(
                "App password",
                type="password",
                placeholder="16-character app password",
                key="app_password_input",
                help="Generate at: https://myaccount.google.com/apppasswords",
            )
            
            # Login
            if st.button("Login", use_container_width=True, type="primary"):
                if email and app_password:
                    with st.spinner("Validating credentials with Gmail..."):
                        is_valid, message = email_auth.validate_credentials(email, app_password)
                    
                    if is_valid:
                        # Credentials are valid
                        email_auth.store_credentials(email, app_password, persist=True)
                        st.success("Logged in successfully!")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(message)
                        st.info("**How to fix:**\n"
                               "1. Go to: https://myaccount.google.com/apppasswords\n"
                               "2. Enable 2-Step Verification if not already\n"
                               "3. Generate a new App Password\n"
                               "4. Copy the 16-character code and try again")
                else:
                    st.error("Please fill both fields")
    
    # Only show Preferences if logged in
    from_email, _ = email_auth.get_credentials()
    
    if from_email:
        # Load preferences from disk
        from modules import preferences
        saved_prefs = preferences.load_preferences()
        
        # Update session state with loaded preferences
        if "email_tone" not in st.session_state:
            st.session_state["email_tone"] = saved_prefs["email_tone"]
        
        # Preferences Section
        with st.sidebar.expander("Preferences", expanded=True):
            # Reload preferences for this section
            saved_prefs = preferences.load_preferences()
            
            # Sender Name
            sender_name = st.text_input(
                "Sender name",
                value=saved_prefs.get("sender_name", ""),
                placeholder="Your name",
                key="sender_name",
            )
            
            # Default Recipient
            st.markdown("**Default recipient email**", help="Your usual recipient (auto-fills the recipient field)")
            default_recipient = st.text_input(
                "Default recipient email",
                value=saved_prefs.get("default_recipient", ""),
                placeholder="manager@company.com",
                key="default_recipient",
                label_visibility="collapsed"
            )
            
            # Default Subject
            st.markdown("**Default subject**", help="Your usual subject line (auto-fills the subject field)")
            default_subject = st.text_input(
                "Default subject",
                value=saved_prefs.get("default_subject", ""),
                placeholder="Daily Task Report",
                key="default_subject",
                label_visibility="collapsed"
            )
            
            # Save Preferences Button
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Save Preferences", use_container_width=True):
                    prefs_to_save = {
                        "email_tone": st.session_state.get("email_tone", "formal"),
                        "sender_name": st.session_state.get("sender_name", ""),
                        "cc_emails": st.session_state.get("cc_emails", ""),
                        "bcc_emails": st.session_state.get("bcc_emails", ""),
                        "subject_prefix": st.session_state.get("subject_prefix", ""),
                        "default_recipient": st.session_state.get("default_recipient", ""),
                        "default_subject": st.session_state.get("default_subject", ""),
                    }
                    
                    if preferences.save_preferences(prefs_to_save):
                        st.success("Preferences saved!")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Failed to save preferences")
            
            with col2:
                if st.button("Clear", use_container_width=True):
                    if preferences.clear_preferences():
                        st.success("Preferences cleared")
                        time.sleep(1)
                        st.rerun()
    
    # System Info
    # with st.sidebar.expander("System Info", expanded=False):
        # ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        # ollama_host = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
        
        # st.markdown(f"""
        # **Model:** {ollama_model}  
        # **Ollama:** {ollama_host}
        
        # **Features:**
        # - 🤖 AI-refined emails
        # - 📋 Task extraction
        # - 🎭 Multiple tone support
        # - 📧 HTML email formatting
        # """)


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


def main():
    apply_custom_css()
    sidebar_credentials()
    
    # Main header
    st.markdown('<h1 class="main-header">Email Automation System</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Transform your work log into professional email reports, instantly.</p>',
        unsafe_allow_html=True
    )
    
    # Instructions
    with st.expander("How to use", expanded=False):
        st.markdown("""
        **Step 1:** Configure Gmail credentials in the sidebar (one-time setup)
        
        **Step 2:** Select email tone and template (optional)
        
        **Step 3:** Enter recipient email address
        
        **Step 4:** Enter email subject (or use auto-generated)
        
        **Step 5:** Write your work log:
        - List your completed tasks
        - Use any format: bullets, numbers, or plain text
        
        **Step 6:** Choose an action:
        - **Send**: Send your work log as-is (no AI refinement)
        - **Refine**: Preview AI-polished version before sending
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
    
    st.markdown("### Send your emails easily")
    
    # Check if user is logged in
    from_email, _ = email_auth.get_credentials()
    
    # Load preferences only if logged in
    from modules import preferences
    if from_email:
        saved_prefs = preferences.load_preferences()
    else:
        # Use defaults when not logged in
        saved_prefs = {
            "email_tone": "formal",
            "sender_name": "",
            "default_recipient": "",
            "default_subject": "",
        }
    
    # Email Tone and Template selector side-by-side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Email tone**", help="Choose the tone for your email")
        
        tone_display = ["Formal", "Neutral", "Friendly"]
        tone_values = ["formal", "neutral", "friendly"]
        
        # Get current saved tone from preferences
        current_tone = saved_prefs.get("email_tone", "formal")
        
        # Find index of current tone
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
        
        # Convert displayed value back to lowercase for storage
        email_tone = tone_values[tone_display.index(email_tone_display)]
        
        # Sync with session state
        st.session_state["email_tone"] = email_tone
    
    with col2:
        st.markdown("**Select template**", help="Choose a pre-made template or start from scratch")
        template_choice = st.selectbox(
            "Select template",
            options=list(example_templates.keys()),
            index=0,
            key="template_selector",
            label_visibility="collapsed"
        )
    
    # Recipient email field (empty if not logged in)
    st.markdown("**Recipient email**", help="Enter the email address of the recipient")
    recipient_email = st.text_input(
        "Recipient email",
        value=saved_prefs.get("default_recipient", ""),
        placeholder="manager@company.com",
        key="recipient_email_input",
        label_visibility="collapsed"
    )
    
    # Subject field (empty if not logged in)
    st.markdown("**Subject**", help="Enter email subject (leave blank for auto-generated)")
    subject_input = st.text_input(
        "Subject",
        value=saved_prefs.get("default_subject", ""),
        placeholder="Daily Task Report (auto-generated if left blank)",
        key="subject_input",
        label_visibility="collapsed"
    )
    
    # Load template if selected
    if template_choice != "Custom":
        initial_value = example_templates[template_choice]
    else:
        initial_value = st.session_state.get("last_prompt", "")
    
    # Your work log field
    st.markdown("**Your work log**", help="List your completed tasks and activities")
    raw_prompt = st.text_area(
        "Your work log",
        value=initial_value,
        height=250,
        placeholder="Today's tasks:\n- Task 1\n- Task 2\n- Task 3",
        key="raw_prompt_input",
        label_visibility="collapsed"
    )
    
    # Save to session
    st.session_state["last_prompt"] = raw_prompt
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        send_button = st.button(
            "Send",
            use_container_width=True,
            help="Send your work log without refinement"
        )
    
    with col2:
        refine_button = st.button(
            "Refine",
            use_container_width=True,
            help="Preview polished version before sending"
        )
    
    with col3:
        refine_and_send_button = st.button(
            "Refine & Send",
            type="primary",
            use_container_width=True,
            help="Generate refined email and send to your desired email address"
        )
    
    # Validate credentials for all actions
    if send_button or refine_button or refine_and_send_button:
        from_email, app_password = email_auth.get_credentials()
        if not from_email or not app_password:
            st.error("Please configure Gmail credentials in the sidebar first.")
            st.stop()
        
        # Validate recipient email
        if not recipient_email or not recipient_email.strip():
            st.error("Please enter a recipient email address.")
            st.stop()
        
        if not raw_prompt.strip():
            st.error("Please enter your work log.")
            st.stop()
    
    # Send
    if send_button:
        handle_send_as_is(recipient_email, subject_input, raw_prompt)
    
    # Refine
    elif refine_button:
        handle_refine(recipient_email, subject_input, raw_prompt)
    
    # Refine & Send
    elif refine_and_send_button:
        handle_refine_and_send(recipient_email, subject_input, raw_prompt)
    
    # Show refined preview
    if "refined_report" in st.session_state:
        show_refined_preview()


def handle_send_as_is(recipient_email: str, subject_input: str, raw_prompt: str):
    """Handle 'Send' button - send work log without any refinement."""
    
    from_email, app_password = email_auth.get_credentials()
    if not from_email or not app_password:
        st.error("Please configure Gmail credentials in the sidebar first.")
        st.stop()
    
    with st.spinner("Processing your work log..."):
        # Parse only tasks
        tasks = prompt_parser.extract_tasks(raw_prompt)
        
        # Validation
        if not tasks:
            st.error("Could not extract any tasks. Please list your completed work.")
            st.stop()
        
        # Get settings
        sender_name = st.session_state.get("sender_name", "Task Automation System")
        cc_emails = st.session_state.get("cc_emails", "")
        bcc_emails = st.session_state.get("bcc_emails", "")
        subject_prefix = st.session_state.get("subject_prefix", "")
        
        # Create simple plain text email
        from datetime import date
        date_str = date.today().strftime("%B %d, %Y")
        
        # Use custom subject if provided, otherwise auto-generate
        if subject_input and subject_input.strip():
            subject = subject_input.strip()
        else:
            subject = f"Daily Task Report - {date_str}"
        
        # Apply subject prefix if set
        if subject_prefix.strip():
            subject = f"{subject_prefix.strip()} {subject}"
        
        # Create plain text body
        text_body = f"""Hello,

Here is my work log for {date_str}:

"""
        for i, task in enumerate(tasks, 1):
            text_body += f"{i}. {task}\n"
        
        text_body += f"""

Best regards,
{sender_name}

---
This report was sent via Task Automation System.
"""
        
        # Create simple HTML version
        task_items = "\n".join(f"<li>{task}</li>" for task in tasks)
        html_body = f"""<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Hello,</p>
    
    <p>Here is my work log for <strong>{date_str}</strong>:</p>
    
    <ol>
        {task_items}
    </ol>
    
    <p>Best regards,<br>
    <strong>{sender_name}</strong></p>
    
    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
    <p style="font-size: 0.9em; color: #666;">
        <em>This report was sent via Task Automation System.</em>
    </p>
</body>
</html>"""
    
    # Show preview
    st.markdown("---")
    st.markdown("### Sending Email")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("**To:**")
        if cc_emails.strip():
            st.markdown("**CC:**")
        if bcc_emails.strip():
            st.markdown("**BCC:**")
        st.markdown("**Subject:**")
        st.markdown("**Tasks:**")
        st.markdown("**Type:**")
    
    with col2:
        st.markdown(f"`{recipient_email}`")
        if cc_emails.strip():
            st.markdown(f"`{cc_emails}`")
        if bcc_emails.strip():
            st.markdown(f"`{bcc_emails}`")
        st.markdown(f"`{subject}`")
        st.markdown(f"`{len(tasks)} tasks`")
        st.markdown(f"`Plain (no AI refinement)`")
    
    # Send email
    try:
        from_email, app_password = email_auth.get_credentials()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Preparing email...")
        progress_bar.progress(25)
        time.sleep(0.3)
        
        status_text.text("Authenticating with Gmail...")
        progress_bar.progress(50)
        time.sleep(0.3)
        
        status_text.text("Sending email...")
        progress_bar.progress(75)
        
        # Include CC/BCC in send
        email_sender.send_email(
            from_email=from_email,
            app_password=app_password,
            to_email=recipient_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails,
        )
        
        progress_bar.progress(100)
        status_text.text("Email sent successfully!")
        
        st.success(f"**Email sent successfully to {recipient_email}!**")
        st.snow()
        
        time.sleep(2)
        st.session_state["last_prompt"] = ""
        st.info("Resetting form...")
        time.sleep(1)
        st.rerun()
    
    except Exception as e:
        st.error("**Failed to send email**")
        st.error(f"**Error:** {str(e)}")


def handle_refine(recipient_email: str, subject_input: str, raw_prompt: str):
    """Handle 'Refine' button - generate AI-refined email and show preview."""
    
    from_email, app_password = email_auth.get_credentials()
    if not from_email or not app_password:
        st.error("Please configure Gmail credentials in the sidebar first.")
        st.stop()
    
    with st.spinner("Refining your work log with AI..."):
        # Parse only tasks
        tasks = prompt_parser.extract_tasks(raw_prompt)
        
        # Validation
        if not tasks:
            st.error("Could not extract any tasks. Please list your completed work.")
            st.stop()
        
        # Get settings
        tone = st.session_state.get("email_tone", "formal")
        sender_name = st.session_state.get("sender_name", "Task Automation System")
        manager_name_override = st.session_state.get("manager_name_override", "")
        
        # Determine manager name
        if manager_name_override:
            manager_name = manager_name_override
        else:
            manager_name = extract_manager_name_from_email(recipient_email)
        
        # Generate report
        generator = report_generator.get_report_generator()
        report = generator.generate_report(
            recipient_email=recipient_email,
            tasks=tasks,
            manager_name=manager_name,
            tone=tone,
            sender_name=sender_name,
        )
        
        # Use custom subject if provided
        if subject_input and subject_input.strip():
            report.subject = subject_input.strip()
        
        # Apply subject prefix
        subject_prefix = st.session_state.get("subject_prefix", "")
        if subject_prefix.strip():
            report.subject = f"{subject_prefix.strip()} {report.subject}"
        
        # Store in session state for later use
        st.session_state["refined_report"] = report
        st.session_state["refined_recipient"] = recipient_email
        st.session_state["refined_tasks"] = tasks
    
    # Force rerun to show the preview section
    st.rerun()


def handle_refine_and_send(recipient_email: str, subject_input: str, raw_prompt: str):
    """Handle 'Refine & Send' button - existing generate and send behavior."""
    
    from_email, app_password = email_auth.get_credentials()
    if not from_email or not app_password:
        st.error("Please configure Gmail credentials in the sidebar first.")
        st.stop()
    
    with st.spinner("Processing your work log..."):
        # Parse only tasks
        tasks = prompt_parser.extract_tasks(raw_prompt)
        
        # Validation
        if not tasks:
            st.error("Could not extract any tasks. Please list your completed work.")
            st.stop()
        
        # Get settings
        tone = st.session_state.get("email_tone", "formal")
        sender_name = st.session_state.get("sender_name", "Task Automation System")
        manager_name_override = st.session_state.get("manager_name_override", "")
        
        # Get CC/BCC/Subject settings
        cc_emails = st.session_state.get("cc_emails", "")
        bcc_emails = st.session_state.get("bcc_emails", "")
        subject_prefix = st.session_state.get("subject_prefix", "")
        
        # Determine manager name
        if manager_name_override:
            manager_name = manager_name_override
        else:
            manager_name = extract_manager_name_from_email(recipient_email)
        
        # Generate report
        generator = report_generator.get_report_generator()
        report = generator.generate_report(
            recipient_email=recipient_email,
            tasks=tasks,
            manager_name=manager_name,
            tone=tone,
            sender_name=sender_name,
        )
        
        # Use custom subject if provided
        if subject_input and subject_input.strip():
            report.subject = subject_input.strip()
        
        # Apply subject prefix
        if subject_prefix.strip():
            report.subject = f"{subject_prefix.strip()} {report.subject}"
    
    # Show preview
    st.markdown("---")
    st.markdown("### 📧 Email Preview")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("**To:**")
        if cc_emails.strip():
            st.markdown("**CC:**")
        if bcc_emails.strip():
            st.markdown("**BCC:**")
        st.markdown("**Subject:**")
        st.markdown("**Tasks Found:**")
        st.markdown("**Generated By:**")
    
    with col2:
        st.markdown(f"`{recipient_email}`")
        if cc_emails.strip():
            st.markdown(f"`{cc_emails}`")
        if bcc_emails.strip():
            st.markdown(f"`{bcc_emails}`")
        st.markdown(f"`{report.subject}`")
        st.markdown(f"`{len(tasks)} tasks`")
        method = report.metadata.get("generation_method", "unknown") if report.metadata else "unknown"
        st.markdown(f"`{method}`")
    
    # HTML Preview
    with st.expander("View Email Content", expanded=True):
        st.components.v1.html(report.body_html, height=600, scrolling=True)
    
    # Send email immediately
    st.markdown("---")
    st.markdown("### Sending Email...")
    
    try:
        from_email, app_password = email_auth.get_credentials()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Preparing email...")
        progress_bar.progress(25)
        time.sleep(0.3)
        
        status_text.text("Authenticating with Gmail...")
        progress_bar.progress(50)
        time.sleep(0.3)
        
        status_text.text("Sending email...")
        progress_bar.progress(75)
        
        # Include CC/BCC in send
        email_sender.send_email(
            from_email=from_email,
            app_password=app_password,
            to_email=recipient_email,
            subject=report.subject,
            html_body=report.body_html,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails,
        )
        
        progress_bar.progress(100)
        status_text.text("Email sent successfully!")
        
        st.success(f"**Email sent successfully to {recipient_email}!**")
        st.balloons()
        
        time.sleep(2)
        st.session_state["last_prompt"] = ""
        st.info("Resetting form...")
        time.sleep(1)
        st.rerun()
    
    except Exception as e:
        st.error("Failed to send email")
        st.error(f"**Error:** {str(e)}")


def show_refined_preview():
    """Show refined email preview with 'Refine Again' and 'Send' buttons."""
    
    report = st.session_state.get("refined_report")
    recipient_email = st.session_state.get("refined_recipient")
    tasks = st.session_state.get("refined_tasks")
    
    if not report:
        return
    
    # Get CC/BCC for display
    cc_emails = st.session_state.get("cc_emails", "")
    bcc_emails = st.session_state.get("bcc_emails", "")
    
    st.markdown("---")
    st.markdown("### ✨ Refined Email Preview")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("**To:**")
        if cc_emails.strip():
            st.markdown("**CC:**")
        if bcc_emails.strip():
            st.markdown("**BCC:**")
        st.markdown("**Subject:**")
        st.markdown("**Tasks Found:**")
        st.markdown("**Generated By:**")
    
    with col2:
        st.markdown(f"`{recipient_email}`")
        if cc_emails.strip():
            st.markdown(f"`{cc_emails}`")
        if bcc_emails.strip():
            st.markdown(f"`{bcc_emails}`")
        st.markdown(f"`{report.subject}`")
        st.markdown(f"`{len(tasks)} tasks`")
        method = report.metadata.get("generation_method", "unknown") if report.metadata else "unknown"
        st.markdown(f"`{method}`")
    
    # HTML Preview
    with st.expander("View Email Content", expanded=True):
        st.components.v1.html(report.body_html, height=600, scrolling=True)
    
    # Action buttons after preview
    st.markdown("### Choose Action")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("Refine Again", use_container_width=True, key="refine_again_btn"):
            # Clear the refined report and trigger new refinement
            raw_prompt = st.session_state.get("last_prompt", "")
            subject_input = st.session_state.get("subject_input", "")
            recipient = st.session_state.get("refined_recipient")
            del st.session_state["refined_report"]
            handle_refine(recipient, subject_input, raw_prompt)
    
    with col2:
        if st.button("Send", type="primary", use_container_width=True, key="send_refined_btn"):
            # Send the refined email
            send_refined_email(report, recipient_email)
    
    with col3:
        if st.button("Cancel", use_container_width=True, key="cancel_refined_btn"):
            del st.session_state["refined_report"]
            del st.session_state["refined_recipient"]
            del st.session_state["refined_tasks"]
            st.rerun()


def send_refined_email(report, recipient_email: str):
    """Send the refined email that's currently in preview."""
    
    st.markdown("---")
    st.markdown("### Sending Refined Email...")
    
    try:
        from_email, app_password = email_auth.get_credentials()
        
        # Get CC/BCC for sending
        cc_emails = st.session_state.get("cc_emails", "")
        bcc_emails = st.session_state.get("bcc_emails", "")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Preparing email...")
        progress_bar.progress(25)
        time.sleep(0.3)
        
        status_text.text("Authenticating with Gmail...")
        progress_bar.progress(50)
        time.sleep(0.3)
        
        status_text.text("Sending email...")
        progress_bar.progress(75)
        
        # Include CC/BCC in send
        email_sender.send_email(
            from_email=from_email,
            app_password=app_password,
            to_email=recipient_email,
            subject=report.subject,
            html_body=report.body_html,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails,
        )
        
        progress_bar.progress(100)
        status_text.text("Email sent successfully!")
        
        st.success(f"**Email sent successfully to {recipient_email}!**")
        st.balloons()
        
        # Clear session state
        time.sleep(2)
        st.session_state["last_prompt"] = ""
        if "refined_report" in st.session_state:
            del st.session_state["refined_report"]
        if "refined_recipient" in st.session_state:
            del st.session_state["refined_recipient"]
        if "refined_tasks" in st.session_state:
            del st.session_state["refined_tasks"]
        
        st.info("Resetting form...")
        time.sleep(1)
        st.rerun()
    
    except Exception as e:
        st.error("**Failed to send email**")
        st.error(f"**Error:** {str(e)}")


if __name__ == "__main__":
    main()
