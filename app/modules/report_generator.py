# app/modules/report_generator.py (COMPLETE FIXED VERSION)

import os
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# Fix: Get config from environment directly
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")


@dataclass
class EmailReport:
    subject: str
    body_html: str
    metadata: Optional[dict] = None


class ReportGenerator:
    """
    Handles email report generation using Ollama LLM.
    """
    
    def __init__(self, model: str = OLLAMA_MODEL, base_url: str = OLLAMA_HOST):
        self.model = model
        self.base_url = base_url
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize Ollama LLM client."""
        try:
            self.llm = Ollama(
                model=self.model,
                base_url=self.base_url,
                temperature=0.7,
                timeout=60,
            )
            # Test connection
            self.llm.invoke("Hello")
            print(f" Ollama connected: {self.model} at {self.base_url}")
        except Exception as e:
            print(f"  Warning: Could not connect to Ollama: {e}")
            print("   Report generation will use fallback mode.")
            self.llm = None
    
    def _get_prompt_template(self) -> PromptTemplate:
        """
        Load the report generation prompt template.
        """
        template = """You are an expert professional email writer. Generate a polished, well-formatted HTML email report.

**Context:**
- Manager Name: {manager_name}
- Report Date: {report_date}
- Sender Name: {sender_name}
- Email Tone: {tone}

**Tasks Completed:**
{tasks_list}

**Instructions:**
1. Create a professional email with proper HTML structure
2. Use a warm greeting addressing {manager_name}
3. Include a brief intro mentioning the date ({report_date})
4. Present tasks in a clean HTML unordered list (<ul>/<li>)
5. Add a professional closing that matches the {tone} tone
6. Sign off with {sender_name}
7. Keep it concise and scannable

**Output ONLY the complete HTML email body (including <html>, <body> tags). Do not add any explanation or markdown code blocks.**

HTML Email:"""

        return PromptTemplate(
            input_variables=["manager_name", "report_date", "sender_name", "tone", "tasks_list"],
            template=template,
        )
    
    def _generate_subject(self, tasks: List[str], report_date: date) -> str:
        """
        Generate email subject line.
        Added defensive checks for task format
        """
        date_str = report_date.strftime("%b %d, %Y")
        
        # Ensure tasks is valid and not empty
        if not tasks or len(tasks) == 0:
            return f"Daily Task Report - {date_str}"
        
        # Get first task and ensure it's a string
        first_task = tasks[0]
        
        # If first_task is somehow a list, extract the first element
        if isinstance(first_task, list):
            if len(first_task) > 0:
                first_task = str(first_task[0])
            else:
                return f"Daily Task Report - {date_str}"
        
        # Ensure it's a string
        first_task = str(first_task)
        
        # Smart subject based on first task
        if first_task:
            # Extract key action/component
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
    
    def _fallback_generate_email(
        self,
        manager_name: str,
        tasks: List[str],
        report_date: date,
        tone: str = "formal",
        sender_name: str = "Task Automation System",
    ) -> str:
        """
        Fallback HTML generation when LLM is unavailable.
        """
        date_str = report_date.strftime("%B %d, %Y")
        
        # Tone-based variations
        if tone == "formal":
            greeting = f"Dear {manager_name},"
            intro = "Please find below a summary of tasks completed on"
            closing = "Should you require any additional information or clarification, please do not hesitate to reach out."
            sign_off = "Respectfully,"
        elif tone == "friendly":
            greeting = f"Hi {manager_name}!"
            intro = "Here's what I accomplished on"
            closing = "Let me know if you'd like to discuss any of these in detail!"
            sign_off = "Cheers,"
        else:  # neutral
            greeting = f"Hello {manager_name},"
            intro = "Below is a summary of work completed on"
            closing = "Please let me know if you have any questions."
            sign_off = "Best regards,"
        
        # Ensure each task is a string
        task_items = "\n".join(f"          <li>{str(task)}</li>" for task in tasks)
        
        html = f"""<html>
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
        h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
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
        <p>{greeting}</p>
        
        <p>{intro} <strong>{date_str}</strong>:</p>
        
        <ul>
    {task_items}
        </ul>
        
        <p>{closing}</p>
        
        <p>
        {sign_off}<br>
        <strong>{sender_name}</strong>
        </p>
        
        <div class="footer">
        <em>This report was automatically generated by the Task Automation System.</em>
        </div>
    </body>
    </html>"""
        
        return html
    
    def generate_report(
        self,
        recipient_email: str,
        tasks: List[str],
        manager_name: str = "Manager",
        report_date: Optional[date] = None,
        tone: str = "formal",
        sender_name: str = "Task Automation System",
    ) -> EmailReport:
        """
        Generate complete email report.
        
        Args:
            recipient_email: Target email address
            tasks: List of completed tasks
            manager_name: Recipient's name for greeting
            report_date: Date of report (defaults to today)
            tone: Email tone (formal/neutral/friendly)
            sender_name: Name to sign email with
        
        Returns:
            EmailReport with subject and HTML body
        """
        # Validate and clean tasks input
        if not tasks:
            raise ValueError("No tasks provided")
        
        # Flatten nested lists if present
        cleaned_tasks = []
        for task in tasks:
            if isinstance(task, list):
                # If it's a list, flatten it
                for item in task:
                    if item and str(item).strip():
                        cleaned_tasks.append(str(item).strip())
            elif isinstance(task, str):
                if task.strip():
                    cleaned_tasks.append(task.strip())
            else:
                # Convert other types to string
                task_str = str(task).strip()
                if task_str:
                    cleaned_tasks.append(task_str)
        
        # Use cleaned tasks
        tasks = cleaned_tasks
        
        if not tasks:
            raise ValueError("No valid tasks after cleaning")
        
        print(f" Processing {len(tasks)} tasks")
        print(f"   First task type: {type(tasks[0])}")
        print(f"   First task: {tasks[0][:50]}..." if len(tasks[0]) > 50 else f"   First task: {tasks[0]}")
        
        if report_date is None:
            report_date = date.today()
        
        subject = self._generate_subject(tasks, report_date)
        
        # Try LLM generation
        if self.llm is not None:
            try:
                prompt_template = self._get_prompt_template()
                
                # Properly format tasks as string
                tasks_list = "\n".join(f"- {task}" for task in tasks)
                date_str = report_date.strftime("%B %d, %Y")
                
                print(f" Invoking LLM with {len(tasks)} tasks...")
                
                # Format the prompt correctly
                prompt = prompt_template.format(
                    manager_name=manager_name,
                    report_date=date_str,
                    sender_name=sender_name,
                    tone=tone,
                    tasks_list=tasks_list,
                )
                
                # Invoke LLM with string, not template
                body_html = self.llm.invoke(prompt)
                
                print(f" LLM generated {len(body_html)} characters")
                
                # Ensure body_html is a string (handle if LLM returns list)
                if isinstance(body_html, list):
                    body_html = " ".join(str(item) for item in body_html)
                
                # Convert to string just to be safe
                body_html = str(body_html)
                
                # Clean up response if LLM wrapped in markdown (COMPLETELY FIXED)
                if "```html" in body_html:
                    # Extract content between ```html and ```
                    parts = body_html.split("```html")
                    if len(parts) > 1:
                        # Get everything after ```html, then take content before closing ```
                        body_html = parts[1].split("```").strip()
                elif "```" in body_html:
                    # Generic code block
                    parts = body_html.split("```")
                    if len(parts) >= 3:
                        # Content is between first and second ```
                        body_html = parts[1].strip()
                
                # Final strip to remove any extra whitespace
                body_html = body_html.strip()
                
                # Validate HTML has basic structure
                if "<html" in body_html.lower() and "<body" in body_html.lower():
                    print(" LLM generation successful")
                    return EmailReport(
                        subject=subject,
                        body_html=body_html,
                        metadata={"generation_method": "llm", "model": self.model},
                    )
                else:
                    print("  LLM output missing HTML structure, using fallback")
                    
            except Exception as e:
                print(f"  LLM generation failed: {e}, using fallback")
        
        # Fallback generation
        print(" Using fallback email generation")
        body_html = self._fallback_generate_email(
            manager_name=manager_name,
            tasks=tasks,
            report_date=report_date,
            tone=tone,
            sender_name=sender_name,
        )
        
        return EmailReport(
            subject=subject,
            body_html=body_html,
            metadata={"generation_method": "fallback"},
        )


# Global instance (initialized once)
_generator_instance = None


def get_report_generator() -> ReportGenerator:
    """Get or create singleton report generator instance."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = ReportGenerator()
    return _generator_instance


# Convenience function for backward compatibility
def generate_email_report_with_llm(
    recipient_email: str,
    tasks: List[str],
    manager_name: str = "Manager",
    use_fallback_on_error: bool = True,
) -> EmailReport:
    """
    Generate email report (legacy interface).
    """
    generator = get_report_generator()
    return generator.generate_report(
        recipient_email=recipient_email,
        tasks=tasks,
        manager_name=manager_name,
    )
