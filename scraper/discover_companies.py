import argparse
import json
import logging
import re
from pathlib import Path

import requests

from scraper.greenhouse import fetch_greenhouse_jobs
from scraper.lever import fetch_lever_jobs

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

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


def load_existing_tokens(companies_path):
    companies = json.loads(Path(companies_path).read_text())
    return {c["token"] for c in companies if "token" in c}


def main(candidates_path, output_path="discovered_companies.json", companies_path="companies.json", limit=None):
    existing_tokens = load_existing_tokens(companies_path)
    candidates = json.loads(Path(candidates_path).read_text())

    if limit is not None:
        candidates = candidates[:limit]

    matches = []
    skipped = []
    for candidate in candidates:
        try:
            result = classify_company(candidate["name"], candidate["website"], existing_tokens)
        except Exception as e:
            result = {"name": candidate["name"], "reason": f"error: {e}"}

        if "reason" in result:
            skipped.append(result)
        else:
            matches.append(result)

    output = {"matches": matches, "skipped": skipped}
    Path(output_path).write_text(json.dumps(output, indent=2))
    logger.info(
        "Checked %d candidates: %d matches, %d skipped",
        len(candidates), len(matches), len(skipped),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("candidates_path")
    parser.add_argument("output_path", nargs="?", default="discovered_companies.json")
    parser.add_argument("--limit", type=int, default=None, help="only check the first N candidates")
    args = parser.parse_args()

    main(args.candidates_path, args.output_path, limit=args.limit)
