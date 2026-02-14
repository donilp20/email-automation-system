"""AI-powered email generation using Groq API."""
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Optional, List
from dataclasses import dataclass
from datetime import date


@dataclass
class EmailReport:
    subject: str
    body_html: str
    metadata: Optional[dict] = None


@st.cache_resource
def init_groq_client():
    """
    Initialize Groq client with API key from Streamlit secrets.
    Uses Llama 3.1 8B model for fast inference.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=2048,
            groq_api_key=api_key
        )
    except KeyError:
        st.error("Missing GROQ_API_KEY in Streamlit secrets")
        st.stop()
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        st.stop()


def _generate_subject(tasks: List[str], report_date: date) -> str:
    """Generate email subject line."""
    date_str = report_date.strftime("%b %d, %Y")
    
    if not tasks or len(tasks) == 0:
        return f"Daily Task Report - {date_str}"
    
    first_task = str(tasks[0]) if tasks else ""
    
    if first_task:
        # Extract key words
        key_words = []
        for word in first_task.split():
            if len(word) > 4 and word.lower() not in ["fixed", "implemented", "worked", "attended"]:
                key_words.append(word)
                if len(key_words) >= 2:
                    break
        
        if key_words:
            keyword_str = " ".join(key_words[:2])
            return f"Daily Update: {keyword_str} - {date_str}"
    
    return f"Daily Task Report - {date_str}"


def generate_email_report(
    tasks: List[str],
    manager_name: str = "Manager",
    report_date: Optional[date] = None,
    tone: str = "formal",
    sender_name: str = "Donil",
) -> EmailReport:
    """
    Generate complete email report using Groq API.
    
    Args:
        tasks: List of completed tasks
        manager_name: Recipient's name for greeting
        report_date: Date of report (defaults to today)
        tone: Email tone (formal/neutral/friendly)
        sender_name: Name to sign email with
    
    Returns:
        EmailReport with subject and HTML body
    """
    if not tasks:
        raise ValueError("No tasks provided")
    
    # Clean tasks
    cleaned_tasks = []
    for task in tasks:
        if isinstance(task, list):
            for item in task:
                if item and str(item).strip():
                    cleaned_tasks.append(str(item).strip())
        elif task and str(task).strip():
            cleaned_tasks.append(str(task).strip())
    
    tasks = cleaned_tasks
    if not tasks:
        raise ValueError("No valid tasks after cleaning")
    
    if report_date is None:
        report_date = date.today()
    
    date_str = report_date.strftime("%B %d, %Y")
    subject = _generate_subject(tasks, report_date)
    
    try:
        llm = init_groq_client()
        
        # Build system message
        system_prompt = f"""You are a professional email writing assistant. Generate HTML email reports.

Preferences:
- Tone: {tone}
- Date: {date_str}
- Manager Name: {manager_name}
- Sender Name: {sender_name}

Generate a well-formatted HTML email with:
1. Proper HTML structure (<html>, <head>, <body>, <style>)
2. Professional greeting to {manager_name}
3. Brief intro mentioning the date
4. Clean task list using <ul> and <li> tags
5. Professional closing matching the {tone} tone
6. Signature with {sender_name}
7. Inline CSS for styling

IMPORTANT: Return ONLY the complete HTML code. Do NOT wrap it in markdown code blocks or add any explanation."""

        # Format tasks list
        tasks_text = "\n".join(f"- {task}" for task in tasks)
        
        user_prompt = f"""Generate a professional email report for these tasks:

{tasks_text}

Remember to use HTML format with proper styling."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        print(f"Invoking Groq API with {len(tasks)} tasks...")
        response = llm.invoke(messages)
        body_html = response.content
        
        # Clean markdown code blocks if present
        if "```html" in body_html:
            parts = body_html.split("```html")
            if len(parts) > 1:
                body_html = parts[1].split("```").strip()
        elif "```" in body_html:
            parts = body_html.split("```")
            if len(parts) >= 3:
                body_html = parts.strip()[1]
        
        body_html = body_html.strip()
        
        print(f"Groq API generated {len(body_html)} characters")
        
        return EmailReport(
            subject=subject,
            body_html=body_html,
            metadata={"generation_method": "groq", "model": "llama-3.1-8b-instant"},
        )
        
    except Exception as e:
        print(f"Groq API failed: {e}")
        st.error(f"Failed to generate email: {e}")
        raise


# Legacy compatibility
class ReportGenerator:
    """Legacy wrapper for backward compatibility."""
    
    def __init__(self, model: str = None, base_url: str = None):
        print("Using Groq API for email generation (cloud mode)")
    
    def generate_report(
        self,
        recipient_email: str,
        tasks: List[str],
        manager_name: str = "Manager",
        report_date: Optional[date] = None,
        tone: str = "formal",
        sender_name: str = "Donil",
    ) -> EmailReport:
        return generate_email_report(
            tasks=tasks,
            manager_name=manager_name,
            report_date=report_date,
            tone=tone,
            sender_name=sender_name,
        )


_generator_instance = None


def get_report_generator() -> ReportGenerator:
    """Get or create singleton report generator instance (legacy)."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = ReportGenerator()
    return _generator_instance


# Legacy function
def generate_email_report_with_llm(
    recipient_email: str,
    tasks: List[str],
    manager_name: str = "Manager",
    use_fallback_on_error: bool = True,
) -> EmailReport:
    """Generate email report (legacy interface)."""
    return generate_email_report(
        tasks=tasks,
        manager_name=manager_name,
    )
