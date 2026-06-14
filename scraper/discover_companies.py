import re

import requests

from scraper.greenhouse import fetch_greenhouse_jobs
from scraper.lever import fetch_lever_jobs

GREENHOUSE_PATTERNS = [
    re.compile(r"(?:boards|job-boards)\.greenhouse\.io/([a-zA-Z0-9_-]+)"),
    re.compile(r"greenhouse\.io/embed/job_board\?for=([a-zA-Z0-9_-]+)"),
]
LEVER_PATTERN = re.compile(r"jobs\.lever\.co/([a-zA-Z0-9_-]+)")


def extract_ats_token(html):
    for pattern in GREENHOUSE_PATTERNS:
        match = pattern.search(html)
        if match:
            return ("greenhouse", match.group(1))

    match = LEVER_PATTERN.search(html)
    if match:
        return ("lever", match.group(1))

    return None


def classify_company(name, website_url, existing_tokens):
    try:
        response = requests.get(website_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"name": name, "reason": f"failed to fetch website: {e}"}

    result = extract_ats_token(response.text)
    if result is None:
        return {"name": name, "reason": "no greenhouse/lever link found"}

    ats_type, token = result

    if token in existing_tokens:
        return {"name": name, "reason": "duplicate token already in companies.json"}

    try:
        if ats_type == "greenhouse":
            fetch_greenhouse_jobs(name, token)
            careers_url = f"https://job-boards.greenhouse.io/{token}"
        else:
            fetch_lever_jobs(name, token)
            careers_url = f"https://jobs.lever.co/{token}"
    except Exception as e:
        return {"name": name, "reason": f"verification failed: {e}"}

    return {"name": name, "type": ats_type, "token": token, "careers_url": careers_url}
