import re
import json
from typing import List, Tuple, Optional

EMAIL_REGEX = re.compile(
    r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
)

def extract_recipient_email(raw_prompt: str) -> str | None:
    """
    Extract the first email address from the prompt.
    Enhanced to look for 'Send to:', 'Recipient:', etc.
    """
    # First, try specific patterns
    send_to_patterns = [
        r"(?:send\s+to|recipient|to|email\s+(?:to|this\s+report\s+to))[\s:=-]+([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
    ]
    
    for pattern in send_to_patterns:
        match = re.search(pattern, raw_prompt, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Fallback: any email in the prompt
    match = EMAIL_REGEX.search(raw_prompt)
    if match:
        return match.group(1).strip()
    
    return None


def extract_task_lines(raw_prompt: str) -> List[str]:
    """
    Extract candidate task lines from the prompt using heuristics.
    Enhanced to handle more formats and edge cases.
    Returns flat list of strings, not nested lists
    """
    lines = raw_prompt.splitlines()
    tasks: List[str] = []
    
    # Skip lines that are clearly headers/metadata
    skip_patterns = [
        r"^(send\s+to|recipient|to|date|for\s+date)[\s:=-]",
        r"^(today'?s?\s+tasks?|summary|work\s+log|tasks?\s+completed)[\s:]",
    ]
    
    def should_skip_line(line: str) -> bool:
        line_lower = line.lower().strip()
        if not line_lower:
            return True
        for pattern in skip_patterns:
            if re.match(pattern, line_lower):
                return True
        # Skip email lines
        if EMAIL_REGEX.search(line):
            return True
        return False
    
    # First pass: explicit bullet/numbered lines
    for line in lines:
        stripped = line.strip()
        if should_skip_line(line):
            continue
        
        # Dash bullets: "- Task"
        if stripped.startswith("- "):
            task = stripped[2:].strip()
            if task:
                tasks.append(task)
            continue
        
        # Asterisk bullets: "* Task"
        if stripped.startswith("* "):
            task = stripped[2:].strip()
            if task:
                tasks.append(task)
            continue
        
        # Numbered: "1. Task" or "1) Task"
        num_match = re.match(r"^\d+[\.\)]\s+(.+)", stripped)
        if num_match:
            task = num_match.group(1).strip()
            if task:
                tasks.append(task)
            continue
    
    if tasks:
        return tasks
    
    # Second pass: find content after task header keywords
    header_keywords = [
        "today's tasks",
        "tasks completed today",
        "summary of today's work",
        "work log for today",
        "here is what i completed today",
        "completed today",
        "today i",
    ]
    
    normalized_lines = [l.lower() for l in lines]
    start_idx = -1
    
    for idx, l in enumerate(normalized_lines):
        if any(keyword in l for keyword in header_keywords):
            start_idx = idx + 1
            break
    
    if start_idx != -1:
        for line in lines[start_idx:]:
            if should_skip_line(line):
                continue
            stripped = line.strip()
            
            if len(stripped) > 5:
                tasks.append(stripped)
    
    if not tasks:
        for line in lines:
            if should_skip_line(line):
                continue
            stripped = line.strip()
            if len(stripped) > 10:
                tasks.append(stripped)
    
    return tasks

def extract_tasks(text: str) -> list:
    """
    Extract tasks from raw text without requiring 'Send to:' line.
    
    Args:
        text: Raw work log text
        
    Returns:
        List of extracted tasks
    """
    lines = text.strip().split("\n")
    tasks = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip headers/labels
        if line.lower().startswith(("today", "completed", "tasks:", "work log")):
            continue
        
        # Remove bullet points, numbers, etc.
        cleaned = line.lstrip("•-*#123456789.") .strip()
        
        if cleaned:
            tasks.append(cleaned)
    
    return tasks


def parse_prompt(raw_prompt: str) -> Tuple[str | None, List[str]]:
    """
    Main parsing function: returns (recipient_email, tasks).
    Ensures tasks is always a flat list of strings
    """
    email = extract_recipient_email(raw_prompt)
    tasks = extract_task_lines(raw_prompt)
    
    if tasks and isinstance(tasks[0], list):
        # Flatten if somehow nested
        tasks = [item for sublist in tasks for item in sublist]
    
    return email, tasks


# LLM-based fallback parser
def parse_prompt_with_llm_fallback(
    raw_prompt: str,
    llm_client=None,
) -> Tuple[str | None, List[str]]:
    """
    Use regex parser first, fall back to LLM if extraction fails.
    This requires an initialized LLM client (Ollama via LangChain).
    """
    email, tasks = parse_prompt(raw_prompt)
    
    # If regex worked well, return immediately
    if email and len(tasks) >= 3:
        return email, tasks
    
    # Otherwise, use LLM to extract
    if llm_client is None:
        # No LLM available, return regex results anyway
        return email, tasks
    
    try:
        # Prepare prompt for LLM
        llm_prompt = f"""Extract the following from this work log:
1. Recipient email address
2. List of tasks completed

Work log:
{raw_prompt}

Respond in JSON format:
{{
  "recipient_email": "email@example.com",
  "tasks": ["task 1", "task 2", "task 3"]
}}

Only return the JSON, nothing else."""

        response = llm_client.invoke(llm_prompt)
        
        # Parse JSON from LLM response
        response_text = response.strip()
        if response_text.startswith("```"):
            # Extract content between code fences
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
        
        parsed = json.loads(response_text)
        
        llm_email = parsed.get("recipient_email")
        llm_tasks = parsed.get("tasks", [])
        
        # Use LLM results if better than regex
        final_email = llm_email if llm_email else email
        final_tasks = llm_tasks if len(llm_tasks) > len(tasks) else tasks
        
        return final_email, final_tasks
        
    except Exception as e:
        # LLM failed, return regex results
        print(f"LLM fallback failed: {e}")
        return email, tasks
