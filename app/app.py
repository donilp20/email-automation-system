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
            color: #2c3e50;
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
    </style>
    """, unsafe_allow_html=True)


def sidebar_credentials():
    """Handle Gmail credentials in sidebar."""
    st.sidebar.title("⚙️ Configuration")
    
    # NEW: Auto-load credentials on first run
    email_auth.load_saved_credentials()
    
    # Gmail Auth Section
    with st.sidebar.expander("📧 Gmail Credentials", expanded=True):
        st.markdown("**Required for sending emails**")
        
        # Check if credentials are loaded
        from_email, _ = email_auth.get_credentials()
        saved_on_disk = email_auth.credentials_are_saved_on_disk()
        
        # Show current email if loaded
        if from_email:
            st.info(f"Logged in as: **{from_email}**")
            if saved_on_disk:
                st.caption("✅ Credentials are saved locally")
        
        # Email input (pre-filled if loaded)
        email = st.text_input(
            "Gmail address",
            value=from_email if from_email else "",
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save", use_container_width=True):
                if email and app_password:
                    # Store with persistence
                    email_auth.store_credentials(email, app_password, persist=True)
                    st.success("✅ Saved locally!")
                    st.rerun()
                else:
                    st.error("❌ Fill both fields")
        
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                # Clear from memory and disk
                email_auth.clear_credentials(delete_from_disk=True)
                st.success("🗑️ Credentials cleared")
                st.rerun()
        
        # Status indicator
        if from_email:
            st.markdown("**Status:** 🟢 Configured")
            st.caption(f"({from_email})")
        else:
            st.markdown("**Status:** 🔴 Not configured")
    
    # Generation Settings
    with st.sidebar.expander(" Email Settings", expanded=False):
        tone = st.selectbox(
            "Email tone",
            options=["formal", "neutral", "friendly"],
            index=0,
            key="email_tone",
        )
        
        sender_name = st.text_input(
            "Sender name",
            value="Task Automation System",
            key="sender_name",
        )
        
        manager_name = st.text_input(
            "Manager name (optional)",
            placeholder="Auto-detected or use 'Manager'",
            key="manager_name_override",
        )
    
    # System Info
    with st.sidebar.expander(" System Info", expanded=False):
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        ollama_host = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
        
        st.markdown(f"""
        **Model:** {ollama_model}  
        **Ollama:** {ollama_host}
        
        **Features:**
        -  AI-powered email generation
        -  Smart task extraction
        -  Multiple tone support
        - HTML email formatting
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
    with st.expander(" How to use", expanded=False):
        st.markdown("""
        **Step 1:** Configure Gmail credentials in the sidebar (one-time setup)
        
        **Step 2:** Write your work log in natural language:
        - Include recipient email (e.g., "Send to: manager@company.com")
        - List your completed tasks
        - Use any format: bullets, numbers, or plain text
        
        **Step 3:** Click "Generate & Send" - the AI will:
        - Extract recipient and tasks
        - Generate a professional email
        - Send it via Gmail
        
        **Example:**
        ```
        Send to: john.manager@techcorp.com
        
        Today's tasks:
        - Fixed critical navigation bug (3 hours)
        - Implemented dashboard analytics feature
        - Code review and sprint planning
        ```
        """)
    
    # Example templates
    example_templates = {
        "Engineering Update": """Send to: manager@techcorp.com

Today's tasks:
- Fixed critical navigation bug in EasyCatering mobile app, took 3 hours
- Implemented new dashboard feature for restaurant analytics
- Attended sprint planning meeting and code review
- Started working on user authentication module""",
        
        "Design Work": """Send to: lead.designer@company.com

Completed today:
- Created wireframes for new onboarding flow
- Conducted user testing session with 5 participants
- Updated design system documentation
- Reviewed and approved icon set from external designer""",
        
        "Marketing Tasks": """Send to: marketing.head@startup.io

Today I:
- Launched Q1 email campaign to 10k subscribers
- Analyzed social media metrics and prepared report
- Coordinated with design team on new landing page
- Scheduled 3 client demos for next week""",
    }
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("###  Your Work Log")
    
    with col2:
        template_choice = st.selectbox(
            "Email Type",
            options=["Custom"] + list(example_templates.keys()),
            key="template_selector",
        )
    
    # Load template if selected
    if template_choice != "Custom":
        initial_value = example_templates[template_choice]
    else:
        initial_value = st.session_state.get("last_prompt", "")
    
    raw_prompt = st.text_area(
        "Paste your work log here",
        value=initial_value,
        height=250,
        placeholder="Send to: recipient@example.com\n\nToday's tasks:\n- Task 1\n- Task 2\n- Task 3",
        key="raw_prompt_input",
    )
    
    # Save to session
    st.session_state["last_prompt"] = raw_prompt
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        generate_and_send = st.button(
            "Generate & Send",
            type="primary",
            use_container_width=True,
        )
    
    with col2:
        preview_only = st.button(
            "Preview Only",
            use_container_width=True,
        )
    
    with col3:
        if st.button("🗑️"):
            st.session_state["last_prompt"] = ""
            st.rerun()
    
    if generate_and_send or preview_only:
        # Validate credentials if sending
        if generate_and_send:
            from_email, app_password = email_auth.get_credentials()
            if not from_email or not app_password:
                st.error(" Please configure Gmail credentials in the sidebar first.")
                st.stop()
        
        if not raw_prompt.strip():
            st.error(" Please enter your work log.")
            st.stop()
        
        with st.spinner(" Processing your work log..."):
            # Parse prompt
            recipient_email, tasks = prompt_parser.parse_prompt(raw_prompt)
            
            # Validation
            if not recipient_email:
                st.error(" Could not extract recipient email. Please include it like: 'Send to: email@example.com'")
                st.stop()
            
            if not tasks:
                st.error(" Could not extract any tasks. Please list your completed work.")
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
        
        # Display preview
        st.markdown("---")
        st.markdown("### Email Preview")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("**To:**")
            st.markdown("**Subject:**")
            st.markdown("**Tasks Found:**")
            st.markdown("**Generated By:**")
        
        with col2:
            st.markdown(f"`{recipient_email}`")
            st.markdown(f"`{report.subject}`")
            st.markdown(f"`{len(tasks)} tasks`")
            method = report.metadata.get("generation_method", "unknown") if report.metadata else "unknown"
            st.markdown(f"`{method}`")
        
        # HTML Preview
        with st.expander(" View Email Content", expanded=True):
            st.components.v1.html(report.body_html, height=600, scrolling=True)
        
        # Send email immediately
        if generate_and_send:
            st.markdown("---")
            st.markdown("###  Sending Email...")
            
            try:
                from_email, app_password = email_auth.get_credentials()
                
                # Show sending progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Prepare
                status_text.text(" Preparing email...")
                progress_bar.progress(25)
                time.sleep(0.3)
                
                # Step 2: Authenticate
                status_text.text(" Authenticating with Gmail...")
                progress_bar.progress(50)
                time.sleep(0.3)
                
                # Step 3: Send
                status_text.text(" Sending email...")
                progress_bar.progress(75)
                
                # Actually send the email
                email_sender.send_email(
                    from_email=from_email,
                    app_password=app_password,
                    to_email=recipient_email,
                    subject=report.subject,
                    html_body=report.body_html,
                )
                
                # Step 4: Complete
                progress_bar.progress(100)
                status_text.text(" Email sent successfully!")
                
                # Success!
                st.success(f" **Email sent successfully to {recipient_email}!**")
                st.balloons()
                
                # Wait and reset
                time.sleep(2)
                st.session_state["last_prompt"] = ""
                st.info(" Resetting form...")
                time.sleep(1)
                st.rerun()
            
            except Exception as e:
                st.error(" **Failed to send email**")
                
                # Show detailed error
                error_msg = str(e)
                st.error(f"**Error:** {error_msg}")
                
                # Provide troubleshooting based on error type
                if "Authentication" in error_msg or "535" in error_msg:
                    st.warning("""
                    **Authentication Issue Detected**
                    
                    This usually means your app password is incorrect or expired.
                    
                    **Quick Fix:**
                    1. Go to https://myaccount.google.com/apppasswords
                    2. Delete the old "Task Automation" password
                    3. Create a new app password
                    4. Copy it and update in the sidebar
                    5. Click Save and try again
                    """)
                elif "Connection" in error_msg or "timed out" in error_msg or "refused" in error_msg:
                    st.warning("""
                    **Network Connection Issue**
                    
                    - Check your internet connection
                    - Verify Docker can access the internet
                    - Make sure no firewall is blocking port 587
                    - Try restarting Docker Desktop (on Mac)
                    """)
                else:
                    with st.expander(" Full Troubleshooting Guide"):
                        st.markdown(f"""
                        ### Common Gmail SMTP Issues:
                        
                        **1. Invalid App Password (Error 535)**
                        - Generate new app password: https://myaccount.google.com/apppasswords
                        - Make sure 2FA is enabled first
                        - Copy the 16-character password exactly (no spaces)
                        
                        **2. Wrong Email Address**
                        - Verify the "from" email matches your Gmail exactly
                        - Check for typos in the sidebar
                        
                        **3. Gmail Security Blocking**
                        - Check your Gmail security settings
                        - Look for "suspicious sign-in" alerts
                        - Approve the sign-in if prompted
                        
                        **4. Network/Firewall Issues**
                        - Ensure port 587 is not blocked
                        - Try disabling VPN temporarily
                        - Check Docker network settings
                        
                        **Current Configuration:**
                        - From: {from_email}
                        - To: {recipient_email}
                        - SMTP: smtp.gmail.com:587
                        
                        **Full Error:**
                        ```
                        {error_msg}
                        ```
                        """)


if __name__ == "__main__":
    main()
