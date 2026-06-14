# Company Discovery Script Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `scraper/discover_companies.py`, a standalone CLI tool that takes a list of candidate companies (name + website URL), detects which ones use Greenhouse or Lever, and writes a review file of ready-to-use `companies.json` entries plus a list of skipped companies with reasons.

**Architecture:** Three pure/composable pieces in one file: `extract_ats_token(html)` (regex-based ATS detection), `classify_company(name, website_url, existing_tokens)` (fetch + detect + verify a single candidate), and `main(...)` (CLI entry point that loads input/output files and loops over candidates with per-candidate error handling, mirroring `scraper/run.py`).

**Tech Stack:** Python, `requests` (already a dependency), pytest (existing test suite, no new dependencies).

---

### Task 1: ATS token extraction

**Files:**
- Create: `scraper/discover_companies.py`
- Test: `tests/test_discover_companies.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_discover_companies.py`:

```python
import pytest

from scraper.discover_companies import extract_ats_token


@pytest.mark.parametrize(
    "html, expected",
    [
        (
            '<a href="https://job-boards.greenhouse.io/examplebio">Careers</a>',
            ("greenhouse", "examplebio"),
        ),
        (
            '<a href="https://boards.greenhouse.io/examplebio">Careers</a>',
            ("greenhouse", "examplebio"),
        ),
        (
            '<iframe src="https://www.greenhouse.io/embed/job_board?for=examplebio"></iframe>',
            ("greenhouse", "examplebio"),
        ),
        (
            '<a href="https://jobs.lever.co/examplebio">Careers</a>',
            ("lever", "examplebio"),
        ),
        (
            "<html><body>No jobs here</body></html>",
            None,
        ),
        (
            '<a href="https://jobs.lever.co/examplebio">Careers</a>'
            '<a href="https://job-boards.greenhouse.io/examplebio2">Careers</a>',
            ("greenhouse", "examplebio2"),
        ),
    ],
)
def test_extract_ats_token(html, expected):
    assert extract_ats_token(html) == expected
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_discover_companies.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.discover_companies'`

- [ ] **Step 3: Implement `scraper/discover_companies.py`**

Create `scraper/discover_companies.py`:

```python
import re

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_discover_companies.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add scraper/discover_companies.py tests/test_discover_companies.py
git commit -m "feat: add ATS token extraction for company discovery"
```

---

### Task 2: Classify a single company

**Files:**
- Modify: `scraper/discover_companies.py`
- Test: `tests/test_discover_companies.py`

- [ ] **Step 1: Write the failing tests**

Add to the top of `tests/test_discover_companies.py` (after the existing `import pytest` line, before the `from scraper.discover_companies import ...` line):

```python
import requests

import scraper.discover_companies as discover_module
```

Then update the existing import line:

```python
from scraper.discover_companies import classify_company, extract_ats_token
```

Then add this helper class and these tests at the end of `tests/test_discover_companies.py`:

```python
class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def test_classify_company_greenhouse_match(monkeypatch):
    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse(
            '<a href="https://job-boards.greenhouse.io/examplebio">Careers</a>'
        ),
    )
    monkeypatch.setattr(discover_module, "fetch_greenhouse_jobs", lambda name, token: [])

    result = classify_company("Example Biosciences", "https://examplebio.com/careers", set())

    assert result == {
        "name": "Example Biosciences",
        "type": "greenhouse",
        "token": "examplebio",
        "careers_url": "https://job-boards.greenhouse.io/examplebio",
    }


def test_classify_company_lever_match(monkeypatch):
    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse(
            '<a href="https://jobs.lever.co/examplebio">Careers</a>'
        ),
    )
    monkeypatch.setattr(discover_module, "fetch_lever_jobs", lambda name, token: [])

    result = classify_company("Example Biosciences", "https://examplebio.com/careers", set())

    assert result == {
        "name": "Example Biosciences",
        "type": "lever",
        "token": "examplebio",
        "careers_url": "https://jobs.lever.co/examplebio",
    }


def test_classify_company_no_ats_link(monkeypatch):
    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse("<html><body>No jobs here</body></html>"),
    )

    result = classify_company("OtherCo", "https://otherco.com/careers", set())

    assert result == {"name": "OtherCo", "reason": "no greenhouse/lever link found"}


def test_classify_company_duplicate_token(monkeypatch):
    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse(
            '<a href="https://job-boards.greenhouse.io/examplebio">Careers</a>'
        ),
    )

    result = classify_company("DupeCo", "https://dupeco.com/careers", {"examplebio"})

    assert result == {"name": "DupeCo", "reason": "duplicate token already in companies.json"}


def test_classify_company_website_fetch_failure(monkeypatch):
    def fake_get(url, timeout):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(discover_module.requests, "get", fake_get)

    result = classify_company("BrokenCo", "https://brokenco.com/careers", set())

    assert result["name"] == "BrokenCo"
    assert result["reason"].startswith("failed to fetch website:")


def test_classify_company_verification_failure(monkeypatch):
    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse(
            '<a href="https://job-boards.greenhouse.io/examplebio">Careers</a>'
        ),
    )

    def fake_fetch(name, token):
        raise requests.HTTPError("404 Client Error")

    monkeypatch.setattr(discover_module, "fetch_greenhouse_jobs", fake_fetch)

    result = classify_company("Example Biosciences", "https://examplebio.com/careers", set())

    assert result["name"] == "Example Biosciences"
    assert result["reason"].startswith("verification failed:")
```

- [ ] **Step 2: Run tests to verify the new tests fail**

Run: `python -m pytest tests/test_discover_companies.py -v`
Expected: FAIL — `ImportError: cannot import name 'classify_company' from 'scraper.discover_companies'`

- [ ] **Step 3: Implement `classify_company`**

Replace the single import line at the top of `scraper/discover_companies.py` (`import re`) with:

```python
import re

import requests

from scraper.greenhouse import fetch_greenhouse_jobs
from scraper.lever import fetch_lever_jobs
```

Then add this function at the end of `scraper/discover_companies.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_discover_companies.py -v`
Expected: PASS (12 tests: 6 from Task 1 + 6 new)

- [ ] **Step 5: Commit**

```bash
git add scraper/discover_companies.py tests/test_discover_companies.py
git commit -m "feat: classify candidate companies as Greenhouse or Lever"
```

---

### Task 3: CLI entry point

**Files:**
- Modify: `scraper/discover_companies.py`
- Test: `tests/test_discover_companies.py`

- [ ] **Step 1: Write the failing test**

Add to the imports at the top of `tests/test_discover_companies.py` (alongside the existing `import pytest` line):

```python
import json
```

Then update the import from `scraper.discover_companies` to include `main`:

```python
from scraper.discover_companies import classify_company, extract_ats_token, main
```

Then add this test at the end of `tests/test_discover_companies.py`:

```python
def test_main_writes_discovered_companies(tmp_path, monkeypatch):
    companies_path = tmp_path / "companies.json"
    companies_path.write_text(json.dumps([
        {
            "name": "Existing Co",
            "type": "greenhouse",
            "token": "existingco",
            "careers_url": "https://job-boards.greenhouse.io/existingco",
        },
    ]))

    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(json.dumps([
        {"name": "Example Biosciences", "website": "https://examplebio.com/careers"},
        {"name": "OtherCo", "website": "https://otherco.com/careers"},
    ]))

    output_path = tmp_path / "discovered_companies.json"

    responses = {
        "https://examplebio.com/careers": '<a href="https://job-boards.greenhouse.io/examplebio">Careers</a>',
        "https://otherco.com/careers": "<html><body>No jobs here</body></html>",
    }

    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse(responses[url]),
    )
    monkeypatch.setattr(discover_module, "fetch_greenhouse_jobs", lambda name, token: [])

    main(
        candidates_path=str(candidates_path),
        output_path=str(output_path),
        companies_path=str(companies_path),
    )

    data = json.loads(output_path.read_text())

    assert data["matches"] == [
        {
            "name": "Example Biosciences",
            "type": "greenhouse",
            "token": "examplebio",
            "careers_url": "https://job-boards.greenhouse.io/examplebio",
        }
    ]
    assert data["skipped"] == [
        {"name": "OtherCo", "reason": "no greenhouse/lever link found"}
    ]
```

- [ ] **Step 2: Run tests to verify the new test fails**

Run: `python -m pytest tests/test_discover_companies.py -v`
Expected: FAIL — `ImportError: cannot import name 'main' from 'scraper.discover_companies'`

- [ ] **Step 3: Implement `main` and CLI entry point**

Replace the import block at the top of `scraper/discover_companies.py` with:

```python
import json
import logging
import re
import sys
from pathlib import Path

import requests

from scraper.greenhouse import fetch_greenhouse_jobs
from scraper.lever import fetch_lever_jobs

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
```

Then add this code at the end of `scraper/discover_companies.py`:

```python
def load_existing_tokens(companies_path):
    companies = json.loads(Path(companies_path).read_text())
    return {c["token"] for c in companies if "token" in c}


def main(candidates_path, output_path="discovered_companies.json", companies_path="companies.json"):
    existing_tokens = load_existing_tokens(companies_path)
    candidates = json.loads(Path(candidates_path).read_text())

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
    output_arg = sys.argv[2] if len(sys.argv) > 2 else "discovered_companies.json"
    main(sys.argv[1], output_arg)
```

- [ ] **Step 4: Run the full test suite to verify everything passes**

Run: `python -m pytest -q`
Expected: PASS (20 tests: 7 existing + 13 from `tests/test_discover_companies.py` — 6 from Task 1 + 6 from Task 2 + 1 new in Task 3)

- [ ] **Step 5: Commit**

```bash
git add scraper/discover_companies.py tests/test_discover_companies.py
git commit -m "feat: add CLI entry point for company discovery script"
```

---

## Notes

- This script is not wired into `scraper/run.py` or the scheduled scrape
  workflow — it's a standalone tool the user runs manually to generate
  candidate `companies.json` entries.
- Usage: `python -m scraper.discover_companies candidates.json [discovered_companies.json]`.
- The user is responsible for compiling `candidates.json` and for reviewing
  and merging entries from `discovered_companies.json` into `companies.json`.
