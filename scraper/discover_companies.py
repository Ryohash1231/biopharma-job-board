import argparse
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from scraper.ashby import fetch_ashby_jobs
from scraper.greenhouse import fetch_greenhouse_jobs
from scraper.lever import fetch_lever_jobs

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

GREENHOUSE_PATTERNS = [
    re.compile(r"greenhouse\.io/embed/job_board/js\?for=([a-zA-Z0-9_-]+)"),
    re.compile(r"greenhouse\.io/embed/job_board\?for=([a-zA-Z0-9_-]+)"),
    re.compile(r"boards-api\.greenhouse\.io/v1/boards/([a-zA-Z0-9_-]+)/jobs"),
    re.compile(r"(?:boards|job-boards)\.greenhouse\.io/([a-zA-Z0-9_-]+)"),
]
LEVER_PATTERN = re.compile(r"jobs\.lever\.co/([a-zA-Z0-9_-]+)")
ASHBY_PATTERN = re.compile(r"jobs\.ashbyhq\.com/([a-zA-Z0-9_-]+)")


def extract_ats_token(html):
    for pattern in GREENHOUSE_PATTERNS:
        match = pattern.search(html)
        if match:
            return ("greenhouse", match.group(1))

    match = LEVER_PATTERN.search(html)
    if match:
        return ("lever", match.group(1))

    match = ASHBY_PATTERN.search(html)
    if match:
        return ("ashby", match.group(1))

    return None


def classify_company(name, website_url, existing_tokens):
    try:
        response = requests.get(
            website_url,
            timeout=10,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return {"name": name, "reason": f"failed to fetch website: {e}"}

    result = extract_ats_token(response.text)
    if result is None:
        return {"name": name, "reason": "no greenhouse/lever/ashby link found"}

    ats_type, token = result

    if token in existing_tokens:
        return {"name": name, "reason": "duplicate token already in companies.json"}

    try:
        if ats_type == "greenhouse":
            fetch_greenhouse_jobs(name, token)
            careers_url = f"https://job-boards.greenhouse.io/{token}"
        elif ats_type == "lever":
            fetch_lever_jobs(name, token)
            careers_url = f"https://jobs.lever.co/{token}"
        else:
            fetch_ashby_jobs(name, token)
            careers_url = f"https://jobs.ashbyhq.com/{token}"
    except Exception as e:
        return {"name": name, "reason": f"verification failed: {e}"}

    return {"name": name, "type": ats_type, "token": token, "careers_url": careers_url}


def load_existing_tokens(companies_path):
    companies = json.loads(Path(companies_path).read_text())
    return {c["token"] for c in companies if "token" in c}


def _classify_candidate(candidate, existing_tokens):
    try:
        return classify_company(candidate["name"], candidate["website"], existing_tokens)
    except Exception as e:
        return {"name": candidate["name"], "reason": f"error: {e}"}


def main(candidates_path, output_path="discovered_companies.json", companies_path="companies.json", limit=None, workers=10):
    existing_tokens = load_existing_tokens(companies_path)
    candidates = json.loads(Path(candidates_path).read_text())

    if limit is not None:
        candidates = candidates[:limit]

    matches = []
    skipped = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = executor.map(
            lambda candidate: _classify_candidate(candidate, existing_tokens), candidates
        )
        for result in results:
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
    parser.add_argument("--workers", type=int, default=10, help="number of concurrent workers")
    args = parser.parse_args()

    main(args.candidates_path, args.output_path, limit=args.limit, workers=args.workers)
