# scripts/generate_dataset.py

import csv
import json
import os
import random
import textwrap
from datetime import date, timedelta

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "data")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "synthetic_dataset.csv")

RANDOM_SEED = 42
MAX_ROWS = 1000

MANAGERS = [
    ("john.manager@techcorp.com", "John"),
    ("sarah.lead@ecomlabs.io", "Sarah"),
    ("priya.pm@finstack.io", "Priya"),
    ("alex.engineering@foodops.co", "Alex"),
    ("meera.manager@easycatering.in", "Meera"),
    ("rahul.lead@mobilityx.com", "Rahul"),
]

SIGN_OFFS = [
    "Best regards",
    "Kind regards",
    "Thanks and regards",
    "Warm regards",
    "Sincerely",
]

TONE_OPTIONS = ["formal", "neutral", "friendly"]

TASK_TEMPLATES = [
    "Fixed {severity} bug in {component} module, took {hours} hours",
    "Implemented {feature} feature for {area}",
    "Attended {meeting_type} meeting and {extra}",
    "Reviewed pull requests for {repo_name}",
    "Refactored {component} for better {quality}",
    "Worked on {feature} integration with {service}",
    "Investigated {issue_type} reported by {stakeholder}",
    "Updated documentation for {component}",
]

SEVERITIES = ["critical", "high-priority", "medium-priority", "blocking"]
COMPONENTS = [
    "navigation",
    "payments",
    "auth",
    "reporting",
    "analytics dashboard",
    "order management",
]
FEATURES = [
    "new dashboard",
    "sales summary",
    "user activity",
    "order tracking",
    "restaurant analytics",
]
AREAS = ["restaurant analytics", "admin portal", "mobile app", "partner dashboard"]
MEETING_TYPES = ["sprint planning", "daily standup", "retrospective", "client sync"]
EXTRAS = [
    "shared implementation details",
    "discussed blockers",
    "reviewed timelines",
    "clarified requirements",
]
REPOS = [
    "easycatering-mobile",
    "easycatering-backend",
    "analytics-service",
    "notification-service",
]
QUALITIES = ["performance", "readability", "maintainability", "test coverage"]
ISSUE_TYPES = ["intermittent login failures", "slow dashboard load times", "email delivery issues"]
STAKEHOLDERS = ["support team", "client", "QA team", "internal users"]
SERVICES = ["Gmail SMTP", "Stripe", "Razorpay", "Twilio", "Firebase"]


def random_date_within_last_n_days(n: int = 7) -> date:
    """Pick a random recent date, for more realistic email contexts."""
    today = date.today()
    delta = random.randint(0, n)
    return today - timedelta(days=delta)


def generate_task() -> str:
    template = random.choice(TASK_TEMPLATES)
    return template.format(
        severity=random.choice(SEVERITIES),
        component=random.choice(COMPONENTS),
        hours=random.randint(1, 5),
        feature=random.choice(FEATURES),
        area=random.choice(AREAS),
        meeting_type=random.choice(MEETING_TYPES),
        extra=random.choice(EXTRAS),
        repo_name=random.choice(REPOS),
        quality=random.choice(QUALITIES),
        issue_type=random.choice(ISSUE_TYPES),
        stakeholder=random.choice(STAKEHOLDERS),
        service=random.choice(SERVICES),
    )


def generate_tasks(min_tasks=3, max_tasks=7):
    count = random.randint(min_tasks, max_tasks)
    return [generate_task() for _ in range(count)]


def format_tasks_section(tasks, style: int) -> str:
    """
    Different bullet styles / formats to stress-test parser:
    style 0: dash bullets
    style 1: asterisk bullets
    style 2: numbered list
    style 3: inline with commas
    """
    if style == 0:
        # "- Task ..."
        return "\n".join(f"- {t}" for t in tasks)
    elif style == 1:
        # "* Task ..."
        return "\n".join(f"* {t}" for t in tasks)
    elif style == 2:
        # "1. Task..."
        lines = [f"{i}. {t}" for i, t in enumerate(tasks, start=1)]
        return "\n".join(lines)
    else:
        # inline, comma-separated
        return ", ".join(tasks)


def generate_prompt(recipient_email: str, tasks, date_str: str) -> str:
    """
    Create realistic prompt variants with different "send to" styles, spacing, etc.
    """
    send_to_variants = [
        f"Send to: {recipient_email}",
        f"Recipient: {recipient_email}",
        f"To - {recipient_email}",
        f"Email this report to {recipient_email}",
    ]
    header = random.choice(send_to_variants)

    intro_variants = [
        "Today's tasks:",
        "Summary of today's work:",
        "Here is what I completed today:",
        "Tasks completed today:",
        "Work log for today:",
    ]
    intro = random.choice(intro_variants)

    bullet_style = random.randint(0, 3)
    tasks_block = format_tasks_section(tasks, bullet_style)

    # Add optional date line to increase variety
    maybe_date_line = random.choice(
        [
            "",
            f"Date: {date_str}",
            f"For date: {date_str}",
        ]
    )

    parts = [header]
    if maybe_date_line:
        parts.append(maybe_date_line)
    parts.append("")  # blank line
    parts.append(intro)
    parts.append(tasks_block)

    # Add some leading/trailing whitespace variation
    raw_prompt = "\n".join(parts)
    if random.random() < 0.3:
        raw_prompt = "\n" + raw_prompt
    if random.random() < 0.3:
        raw_prompt = raw_prompt + "\n\nThanks!"

    return raw_prompt


def generate_subject(tasks, date_str: str) -> str:
    """
    Simple subject heuristic based on first task + date.
    """
    first_task = tasks[0]
    short_first = first_task.split(",")[0]
    base_subjects = [
        f"Daily Task Report - {date_str}",
        f"Work Summary for {date_str}",
        f"Today's Progress Update - {date_str}",
        f"Status Report - {date_str}",
        f"Update: {short_first} ({date_str})",
    ]
    return random.choice(base_subjects)


def generate_email_body(
    manager_name: str,
    tasks,
    report_date: date,
    tone: str,
    sender_name: str = "Automated Task Reporter",
) -> str:
    """
    Generate a reasonably professional HTML-like email body.
    This will serve as the "golden" expected output for training/eval.
    """
    date_str = report_date.strftime("%d %b %Y")
    task_items_html = "".join(f"<li>{t}</li>" for t in tasks)

    if tone == "formal":
        greeting = f"Dear {manager_name},"
        closing = "Please let me know if you need any additional details."
    elif tone == "friendly":
        greeting = f"Hi {manager_name},"
        closing = "Happy to share more details if needed!"
    else:  # neutral
        greeting = f"Hello {manager_name},"
        closing = "Feel free to reach out if you have any questions."

    body = f"""
    <html>
      <body>
        <p>{greeting}</p>
        <p>
          Here is a summary of the work completed on <strong>{date_str}</strong>:
        </p>
        <ul>
          {task_items_html}
        </ul>
        <p>{closing}</p>
        <p>Regards,<br>{sender_name}</p>
      </body>
    </html>
    """

    # Normalize indentation
    return textwrap.dedent(body).strip()


def main():
    random.seed(RANDOM_SEED)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = [
        "id",
        "raw_prompt",
        "recipient_email",
        "tasks",          # JSON array string
        "subject",
        "email_body",     # HTML
        "tone",
        "language",
        "report_date",
    ]

    with open(OUTPUT_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, MAX_ROWS + 1):
            (recipient_email, manager_first_name) = random.choice(MANAGERS)
            tasks = generate_tasks()
            report_date = random_date_within_last_n_days(10)
            date_str = report_date.isoformat()
            tone = random.choice(TONE_OPTIONS)

            raw_prompt = generate_prompt(recipient_email, tasks, date_str)
            subject = generate_subject(tasks, date_str)
            email_body = generate_email_body(
                manager_name=manager_first_name,
                tasks=tasks,
                report_date=report_date,
                tone=tone,
                sender_name="EasyCatering Automation",
            )

            row = {
                "id": i,
                "raw_prompt": raw_prompt,
                "recipient_email": recipient_email,
                "tasks": json.dumps(tasks, ensure_ascii=False),
                "subject": subject,
                "email_body": email_body,
                "tone": tone,
                "language": "en",
                "report_date": date_str,
            }
            writer.writerow(row)

    print(f"Generated {MAX_ROWS} rows at {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
