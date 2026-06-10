import json
import os
import re

import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"
MAX_HTML_CHARS = 15000


def _clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "svg", "noscript"]):
        tag.decompose()
    return str(soup)[:MAX_HTML_CHARS]


def _extract_json_array(text):
    match = re.search(r"\[.*\]", text.strip(), re.DOTALL)
    if not match:
        raise ValueError(f"No JSON array found in Claude response: {text!r}")
    return json.loads(match.group(0))


def fetch_html_jobs(company_name, careers_url, client=None):
    response = requests.get(
        careers_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()
    cleaned_html = _clean_html(response.text)

    client = client or Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract all job postings from this careers page HTML. "
                    "Return ONLY a JSON array of objects with keys 'title', "
                    "'location', and 'url'. Resolve relative URLs against "
                    f"{careers_url}. If no listings are found, return []. "
                    "Do not include any text outside the JSON array.\n\n"
                    f"HTML:\n{cleaned_html}"
                ),
            }
        ],
    )

    jobs = _extract_json_array(message.content[0].text)
    return [
        {
            "company": company_name,
            "title": job["title"],
            "location": job.get("location", ""),
            "url": job["url"],
        }
        for job in jobs
    ]
