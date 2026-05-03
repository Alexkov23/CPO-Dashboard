"""Google Docs task parser.

Parses text content from Google Docs into structured tasks.

Expected format:
    27.01.2026
    1. + задача выполнена
    2. задача активная
    3. многострочная задача
       продолжение задачи

Rules:
    - Line matching DD.MM.YYYY -> task_date
    - Number prefix (e.g. "1.") -> task number
    - "+" after number -> done=True, status="done"
    - Remaining text -> title
    - Non-numbered continuation lines are appended to previous task
"""

import re
from dataclasses import dataclass
from datetime import date
from urllib.parse import parse_qs, urlparse


@dataclass
class ParsedTask:
    task_date: date
    number: int
    title: str
    done: bool
    status: str  # "done" | "active"


DATE_PATTERN = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})\s*$")
TASK_PATTERN = re.compile(r"^(\d+)\.\s*(\+)?\s*(.+)$")


def parse_doc_url(url: str) -> tuple[str, str]:
    """Extract doc_id and section (tab) from a Google Docs URL.

    Returns (doc_id, section).
    """
    parsed = urlparse(url)
    path = parsed.path

    doc_id_match = re.search(r"/d/([a-zA-Z0-9_-]+)", path)
    if not doc_id_match:
        raise ValueError(f"Cannot extract doc_id from URL: {url}")

    doc_id = doc_id_match.group(1)

    section = ""
    fragment = parsed.fragment
    if fragment:
        tab_match = re.search(r"tab=(t\.[a-zA-Z0-9_]+)", fragment)
        if tab_match:
            section = tab_match.group(1)

    query = parse_qs(parsed.query)
    if not section and "tab" in query:
        section = query["tab"][0]

    return doc_id, section


def parse_tasks_text(text: str) -> list[ParsedTask]:
    """Parse raw text from a Google Doc into a list of tasks."""
    lines = text.split("\n")
    tasks: list[ParsedTask] = []
    current_date: date | None = None
    current_task: ParsedTask | None = None

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        date_match = DATE_PATTERN.match(line)
        if date_match:
            if current_task:
                tasks.append(current_task)
                current_task = None
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year = int(date_match.group(3))
            try:
                current_date = date(year, month, day)
            except ValueError:
                continue
            continue

        task_match = TASK_PATTERN.match(line)
        if task_match and current_date:
            if current_task:
                tasks.append(current_task)

            number = int(task_match.group(1))
            done = task_match.group(2) is not None
            title = task_match.group(3).strip()

            current_task = ParsedTask(
                task_date=current_date,
                number=number,
                title=title,
                done=done,
                status="done" if done else "active",
            )
            continue

        if current_task and current_date:
            current_task.title += " " + line

    if current_task:
        tasks.append(current_task)

    return tasks
