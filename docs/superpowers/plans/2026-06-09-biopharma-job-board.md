# Bay Area Biopharma Job Board Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static job board that aggregates open positions from ~15-25 Bay Area biopharma companies' career pages into one searchable page, updated daily via a scheduled scraper, hosted free on GitHub Pages.

**Architecture:** A Python scraper (`scraper/`) reads `companies.json`, fetches each company's job listings (via the Greenhouse or Lever public JSON APIs where available, or via Claude-assisted HTML extraction otherwise), and writes the combined results to `jobs.json`. A static frontend (`index.html`/`app.js`/`style.css`) loads `jobs.json` and provides client-side search/filter. A GitHub Actions workflow runs the scraper daily and commits updated `jobs.json`.

**Tech Stack:** Python 3.12, `requests`, `beautifulsoup4`, `anthropic` (Claude API), `pytest` + `requests-mock` for testing, vanilla HTML/CSS/JS frontend, GitHub Actions, GitHub Pages.

---

## Background research (already done)

During planning, the live career pages of several companies from the
[biopharmguy Northern California list](https://biopharmguy.com/links/company-by-name-northern-california.php)
were checked. Two distinct, reliable patterns emerged:

1. **Greenhouse-hosted job boards** expose a public JSON API at
   `https://boards-api.greenhouse.io/v1/boards/<token>/jobs`, returning
   `{"jobs": [{"title": ..., "location": {"name": ...}, "absolute_url": ...}], "meta": {"total": N}}`.
   Verified working for:
   - Annexon Biosciences → token `annexonbioscience`
   - Caribou Biosciences → token `cariboubiosciencesinc`

2. **Lever-hosted job boards** expose a public JSON API at
   `https://api.lever.co/v0/postings/<token>?mode=json`, returning a JSON
   array of `{"text": ..., "categories": {"location": ...}, "hostedUrl": ...}`.
   Verified working (returns valid `[]` when no openings) for:
   - Bolt Biotherapeutics → token `boltbio`

3. **Everything else** (custom career pages, PinPoint, Rippling, JobScore,
   etc.) has no consistent structure or public API, so these are handled by
   fetching the HTML and asking Claude to extract a JSON array of
   `{title, location, url}`. Confirmed candidates for this path:
   - BigHat Biosciences → `https://bighatbiosciences.pinpointhq.com/en/jobs`
   - Gordian Biotechnology → `https://ats.rippling.com/gordian-biotechnology/jobs`

Workday-hosted boards (e.g., Cytokinetics) are JS-rendered and out of scope
per the design doc.

---

## Task 1: Project scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `README.md`
- Create: `scraper/__init__.py`

- [ ] **Step 1: Create the directory structure and dependency list**

```bash
mkdir -p scraper tests/fixtures .github/workflows
```

Create `requirements.txt`:

```
requests
beautifulsoup4
anthropic
pytest
requests-mock
```

- [ ] **Step 2: Create `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
```

- [ ] **Step 3: Create `scraper/__init__.py`** (empty file, makes `scraper` a package)

- [ ] **Step 4: Create `README.md`**

```markdown
# Bay Area Biopharma Job Board

Aggregates open positions from Bay Area biopharma companies' career pages
into one searchable page.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-api-key-here
```

## Running the scraper

```bash
python -m scraper.run
```

This reads `companies.json` and writes `jobs.json`.

## Running the frontend locally

```bash
python -m http.server 8000
```

Then open http://localhost:8000/

## Running tests

```bash
pytest
```
```

- [ ] **Step 5: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: dependencies install without error.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .gitignore README.md scraper/__init__.py
git commit -m "Set up project scaffolding"
```

---

## Task 2: Build companies.json

**Files:**
- Create: `companies.json`

The schema is a JSON array of objects. Each object has a `name`, a `type`
(`"greenhouse"`, `"lever"`, or `"html"`), and either a `token` (for
greenhouse/lever) or just a `careers_url` (for html). All entries include
`careers_url` for reference/debugging even when `token` is used.

- [ ] **Step 1: Write the seed entries (already verified)**

Create `companies.json` with these 5 verified entries:

```json
[
  {
    "name": "Annexon Biosciences",
    "type": "greenhouse",
    "token": "annexonbioscience",
    "careers_url": "https://annexonbio.com/jobs/"
  },
  {
    "name": "Caribou Biosciences",
    "type": "greenhouse",
    "token": "cariboubiosciencesinc",
    "careers_url": "https://www.cariboubio.com/careers/jobs/"
  },
  {
    "name": "Bolt Biotherapeutics",
    "type": "lever",
    "token": "boltbio",
    "careers_url": "https://jobs.lever.co/boltbio"
  },
  {
    "name": "BigHat Biosciences",
    "type": "html",
    "careers_url": "https://bighatbiosciences.pinpointhq.com/en/jobs"
  },
  {
    "name": "Gordian Biotechnology",
    "type": "html",
    "careers_url": "https://ats.rippling.com/gordian-biotechnology/jobs"
  }
]
```

- [ ] **Step 2: Research and add more companies (target: 15-25 total)**

For each candidate company below, visit its careers page and determine
which case it falls into, then add an entry to `companies.json`:

- **If the careers page links to `job-boards.greenhouse.io/<token>/...`**:
  add `{"name": ..., "type": "greenhouse", "token": "<token>", "careers_url": <link to their /jobs page>}`.
  Verify by fetching `https://boards-api.greenhouse.io/v1/boards/<token>/jobs`
  and confirming it returns a `{"jobs": [...]}` JSON object (not a 404).

- **If it links to `jobs.lever.co/<token>`**: add
  `{"name": ..., "type": "lever", "token": "<token>", "careers_url": <link>}`.
  Verify by fetching `https://api.lever.co/v0/postings/<token>?mode=json`
  and confirming it returns a JSON array (not a 404).

- **Otherwise** (custom page, PinPoint, Rippling, JobScore, etc.): add
  `{"name": ..., "type": "html", "careers_url": <the job listing page URL>}`.
  Skip if the page is clearly JS-rendered with no listings in the raw HTML
  (test with `curl <url>` — if no job titles appear in the output, skip it).

Candidates to check first (career page entry points already identified):

| Company | Starting URL |
|---|---|
| Allogene Therapeutics | https://careers.jobscore.com/careers/allogene |
| Akero Therapeutics | https://akerotx.com/job-opportunities/ |
| Arsenal Biosciences | https://jobs.arsenalbio.com |
| Adicet Bio | https://www.adicetbio.com/careers/openings/ |
| Assembly Biosciences | https://www.assemblybio.com/careers/opportunities |
| Corcept Therapeutics | https://corcept.com/careers/current-opportunities/ |

If fewer than 15 total companies result from the above, continue down the
[biopharmguy Northern California list](https://biopharmguy.com/links/company-by-name-northern-california.php),
checking each company's `/careers` page using the same method, until the
list has 15-25 entries.

- [ ] **Step 3: Validate the JSON**

Run: `python -c "import json; data = json.load(open('companies.json')); print(len(data), 'companies')"`
Expected: prints a count between 15 and 25, no JSON errors.

- [ ] **Step 4: Commit**

```bash
git add companies.json
git commit -m "Add curated list of biopharma companies"
```

---

## Task 3: Greenhouse fetcher

**Files:**
- Create: `scraper/greenhouse.py`
- Test: `tests/test_greenhouse.py`
- Test fixture: `tests/fixtures/greenhouse_jobs.json`

- [ ] **Step 1: Create the fixture**

Create `tests/fixtures/greenhouse_jobs.json`:

```json
{
  "jobs": [
    {
      "id": 4699427005,
      "title": "Associate Director, Clinical Trial Management",
      "location": {"name": "San Francisco Bay Area"},
      "absolute_url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/4699427005"
    },
    {
      "id": 4684932005,
      "title": "Director, Procurement Strategic Contract Negotiator",
      "location": {"name": "San Francisco Bay Area"},
      "absolute_url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/4684932005"
    }
  ],
  "meta": {"total": 2}
}
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_greenhouse.py`:

```python
import json
from pathlib import Path

from scraper.greenhouse import fetch_greenhouse_jobs

FIXTURE = json.loads(
    Path(__file__).parent.joinpath("fixtures", "greenhouse_jobs.json").read_text()
)


def test_fetch_greenhouse_jobs(requests_mock):
    requests_mock.get(
        "https://boards-api.greenhouse.io/v1/boards/annexonbioscience/jobs",
        json=FIXTURE,
    )

    jobs = fetch_greenhouse_jobs("Annexon Biosciences", "annexonbioscience")

    assert jobs == [
        {
            "company": "Annexon Biosciences",
            "title": "Associate Director, Clinical Trial Management",
            "location": "San Francisco Bay Area",
            "url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/4699427005",
        },
        {
            "company": "Annexon Biosciences",
            "title": "Director, Procurement Strategic Contract Negotiator",
            "location": "San Francisco Bay Area",
            "url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/4684932005",
        },
    ]
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_greenhouse.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.greenhouse'`

- [ ] **Step 4: Write the implementation**

Create `scraper/greenhouse.py`:

```python
import requests


def fetch_greenhouse_jobs(company_name, token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    return [
        {
            "company": company_name,
            "title": job["title"],
            "location": job["location"]["name"],
            "url": job["absolute_url"],
        }
        for job in data.get("jobs", [])
    ]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_greenhouse.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scraper/greenhouse.py tests/test_greenhouse.py tests/fixtures/greenhouse_jobs.json
git commit -m "Add Greenhouse jobs fetcher"
```

---

## Task 4: Lever fetcher

**Files:**
- Create: `scraper/lever.py`
- Test: `tests/test_lever.py`
- Test fixture: `tests/fixtures/lever_jobs.json`

- [ ] **Step 1: Create the fixture**

Create `tests/fixtures/lever_jobs.json`:

```json
[
  {
    "id": "a1b2c3d4-0000-0000-0000-000000000001",
    "text": "Senior Scientist, Protein Engineering",
    "categories": {"location": "Redwood City, CA"},
    "hostedUrl": "https://jobs.lever.co/boltbio/a1b2c3d4-0000-0000-0000-000000000001"
  },
  {
    "id": "a1b2c3d4-0000-0000-0000-000000000002",
    "text": "Research Associate, Antibody Discovery",
    "categories": {"location": "Redwood City, CA"},
    "hostedUrl": "https://jobs.lever.co/boltbio/a1b2c3d4-0000-0000-0000-000000000002"
  }
]
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_lever.py`:

```python
import json
from pathlib import Path

from scraper.lever import fetch_lever_jobs

FIXTURE = json.loads(
    Path(__file__).parent.joinpath("fixtures", "lever_jobs.json").read_text()
)


def test_fetch_lever_jobs(requests_mock):
    requests_mock.get(
        "https://api.lever.co/v0/postings/boltbio?mode=json",
        json=FIXTURE,
    )

    jobs = fetch_lever_jobs("Bolt Biotherapeutics", "boltbio")

    assert jobs == [
        {
            "company": "Bolt Biotherapeutics",
            "title": "Senior Scientist, Protein Engineering",
            "location": "Redwood City, CA",
            "url": "https://jobs.lever.co/boltbio/a1b2c3d4-0000-0000-0000-000000000001",
        },
        {
            "company": "Bolt Biotherapeutics",
            "title": "Research Associate, Antibody Discovery",
            "location": "Redwood City, CA",
            "url": "https://jobs.lever.co/boltbio/a1b2c3d4-0000-0000-0000-000000000002",
        },
    ]


def test_fetch_lever_jobs_empty(requests_mock):
    requests_mock.get(
        "https://api.lever.co/v0/postings/boltbio?mode=json",
        json=[],
    )

    jobs = fetch_lever_jobs("Bolt Biotherapeutics", "boltbio")

    assert jobs == []
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_lever.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.lever'`

- [ ] **Step 4: Write the implementation**

Create `scraper/lever.py`:

```python
import requests


def fetch_lever_jobs(company_name, token):
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    return [
        {
            "company": company_name,
            "title": job["text"],
            "location": job.get("categories", {}).get("location", ""),
            "url": job["hostedUrl"],
        }
        for job in data
    ]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_lever.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scraper/lever.py tests/test_lever.py tests/fixtures/lever_jobs.json
git commit -m "Add Lever jobs fetcher"
```

---

## Task 5: HTML + Claude fetcher

**Files:**
- Create: `scraper/html_extract.py`
- Test: `tests/test_html_extract.py`
- Test fixture: `tests/fixtures/sample_careers_page.html`

- [ ] **Step 1: Create the fixture**

Create `tests/fixtures/sample_careers_page.html`:

```html
<html>
<head><script>var x = 1;</script></head>
<body>
<div class="job">
  <a href="/en/jobs/527616">Scientist II, Cell Line Engineering</a>
  <span class="location">San Mateo, CA</span>
</div>
<div class="job">
  <a href="/en/jobs/484931">Director/Senior Director, Antibody Discovery</a>
  <span class="location">San Mateo, CA</span>
</div>
</body>
</html>
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_html_extract.py`:

```python
import json
from pathlib import Path
from unittest.mock import MagicMock

from scraper.html_extract import fetch_html_jobs, _clean_html, _extract_json_array

SAMPLE_HTML = Path(__file__).parent.joinpath(
    "fixtures", "sample_careers_page.html"
).read_text()

CLAUDE_RESPONSE_TEXT = json.dumps([
    {
        "title": "Scientist II, Cell Line Engineering",
        "location": "San Mateo, CA",
        "url": "https://example.com/en/jobs/527616",
    },
    {
        "title": "Director/Senior Director, Antibody Discovery",
        "location": "San Mateo, CA",
        "url": "https://example.com/en/jobs/484931",
    },
])


def test_clean_html_removes_script_tags():
    cleaned = _clean_html(SAMPLE_HTML)
    assert "<script>" not in cleaned
    assert "Scientist II" in cleaned


def test_extract_json_array_handles_markdown_fences():
    text = f"```json\n{CLAUDE_RESPONSE_TEXT}\n```"
    result = _extract_json_array(text)
    assert result[0]["title"] == "Scientist II, Cell Line Engineering"


def test_fetch_html_jobs(requests_mock):
    requests_mock.get("https://example.com/careers", text=SAMPLE_HTML)

    mock_block = MagicMock()
    mock_block.text = CLAUDE_RESPONSE_TEXT
    mock_message = MagicMock()
    mock_message.content = [mock_block]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    jobs = fetch_html_jobs("BigHat Biosciences", "https://example.com/careers", client=mock_client)

    assert jobs == [
        {
            "company": "BigHat Biosciences",
            "title": "Scientist II, Cell Line Engineering",
            "location": "San Mateo, CA",
            "url": "https://example.com/en/jobs/527616",
        },
        {
            "company": "BigHat Biosciences",
            "title": "Director/Senior Director, Antibody Discovery",
            "location": "San Mateo, CA",
            "url": "https://example.com/en/jobs/484931",
        },
    ]
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_html_extract.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.html_extract'`

- [ ] **Step 4: Write the implementation**

Create `scraper/html_extract.py`:

```python
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_html_extract.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scraper/html_extract.py tests/test_html_extract.py tests/fixtures/sample_careers_page.html
git commit -m "Add Claude-assisted HTML jobs fetcher"
```

---

## Task 6: Orchestrator (scraper/run.py)

**Files:**
- Create: `scraper/run.py`
- Test: `tests/test_run.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_run.py`:

```python
import json

from scraper import run as run_module


def test_run_writes_jobs_and_skips_failures(tmp_path, monkeypatch):
    companies = [
        {
            "name": "GoodCo",
            "type": "greenhouse",
            "token": "goodco",
            "careers_url": "https://goodco.example/careers",
        },
        {
            "name": "BadCo",
            "type": "lever",
            "token": "badco",
            "careers_url": "https://badco.example/careers",
        },
    ]
    companies_path = tmp_path / "companies.json"
    companies_path.write_text(json.dumps(companies))
    output_path = tmp_path / "jobs.json"

    monkeypatch.setattr(
        run_module,
        "fetch_greenhouse_jobs",
        lambda name, token: [
            {
                "company": name,
                "title": "Research Associate",
                "location": "Bay Area",
                "url": "https://goodco.example/jobs/1",
            }
        ],
    )

    def boom(name, token):
        raise RuntimeError("site is down")

    monkeypatch.setattr(run_module, "fetch_lever_jobs", boom)

    run_module.run(companies_path=str(companies_path), output_path=str(output_path))

    data = json.loads(output_path.read_text())
    assert "scraped_at" in data
    assert data["jobs"] == [
        {
            "company": "GoodCo",
            "title": "Research Associate",
            "location": "Bay Area",
            "url": "https://goodco.example/jobs/1",
        }
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_run.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.run'`

- [ ] **Step 3: Write the implementation**

Create `scraper/run.py`:

```python
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from scraper.greenhouse import fetch_greenhouse_jobs
from scraper.lever import fetch_lever_jobs
from scraper.html_extract import fetch_html_jobs

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run(companies_path="companies.json", output_path="jobs.json"):
    companies = json.loads(Path(companies_path).read_text())

    fetchers = {
        "greenhouse": lambda c: fetch_greenhouse_jobs(c["name"], c["token"]),
        "lever": lambda c: fetch_lever_jobs(c["name"], c["token"]),
        "html": lambda c: fetch_html_jobs(c["name"], c["careers_url"]),
    }

    all_jobs = []
    for company in companies:
        try:
            jobs = fetchers[company["type"]](company)
            logger.info("%s: found %d jobs", company["name"], len(jobs))
            all_jobs.extend(jobs)
        except Exception:
            logger.exception("Failed to fetch jobs for %s", company["name"])

    output = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "jobs": all_jobs,
    }
    Path(output_path).write_text(json.dumps(output, indent=2))
    logger.info("Wrote %d total jobs to %s", len(all_jobs), output_path)


if __name__ == "__main__":
    run()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_run.py -v`
Expected: PASS

- [ ] **Step 5: Run the full test suite**

Run: `pytest -v`
Expected: all tests PASS

- [ ] **Step 6: Commit**

```bash
git add scraper/run.py tests/test_run.py
git commit -m "Add scraper orchestrator"
```

---

## Task 7: Frontend

**Files:**
- Create: `index.html`
- Create: `app.js`
- Create: `style.css`
- Create: `jobs.json` (sample data for local testing)

- [ ] **Step 1: Create a sample `jobs.json` for local testing**

Create `jobs.json`:

```json
{
  "scraped_at": "2026-06-09T13:00:00+00:00",
  "jobs": [
    {
      "company": "Annexon Biosciences",
      "title": "Research Associate, Protein Sciences",
      "location": "San Francisco Bay Area",
      "url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/0000000001"
    },
    {
      "company": "Caribou Biosciences",
      "title": "Senior Research Associate, Cell Biology",
      "location": "Berkeley, CA",
      "url": "https://job-boards.greenhouse.io/cariboubiosciencesinc/jobs/0000000002"
    },
    {
      "company": "BigHat Biosciences",
      "title": "Scientist II, Cell Line Engineering",
      "location": "San Mateo, CA",
      "url": "https://bighatbiosciences.pinpointhq.com/en/jobs/527616"
    }
  ]
}
```

This file will be overwritten by the real scraper output once Task 6 is run
end-to-end (or by the GitHub Actions workflow in Task 8).

- [ ] **Step 2: Create `style.css`**

```css
body {
  font-family: system-ui, sans-serif;
  max-width: 900px;
  margin: 2rem auto;
  padding: 0 1rem;
  color: #222;
}

h1 {
  font-size: 1.5rem;
}

#last-updated {
  color: #666;
  font-size: 0.9rem;
  margin-top: -0.5rem;
}

#search {
  width: 100%;
  padding: 0.5rem;
  font-size: 1rem;
  margin-bottom: 1rem;
  box-sizing: border-box;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  text-align: left;
  padding: 0.5rem;
  border-bottom: 1px solid #ddd;
}

th {
  font-size: 0.85rem;
  text-transform: uppercase;
  color: #666;
}
```

- [ ] **Step 3: Create `app.js`**

```javascript
async function init() {
  const response = await fetch('jobs.json');
  const data = await response.json();

  const lastUpdated = document.getElementById('last-updated');
  lastUpdated.textContent = `Last updated: ${new Date(data.scraped_at).toLocaleString()}`;

  const tbody = document.getElementById('jobs-body');
  const searchInput = document.getElementById('search');

  function render(jobs) {
    tbody.innerHTML = '';
    for (const job of jobs) {
      const row = document.createElement('tr');

      const titleCell = document.createElement('td');
      const link = document.createElement('a');
      link.href = job.url;
      link.target = '_blank';
      link.rel = 'noopener';
      link.textContent = job.title;
      titleCell.appendChild(link);

      const companyCell = document.createElement('td');
      companyCell.textContent = job.company;

      const locationCell = document.createElement('td');
      locationCell.textContent = job.location;

      row.append(titleCell, companyCell, locationCell);
      tbody.appendChild(row);
    }
  }

  function applyFilter() {
    const query = searchInput.value.toLowerCase();
    const filtered = data.jobs.filter(job =>
      job.title.toLowerCase().includes(query) ||
      job.company.toLowerCase().includes(query) ||
      job.location.toLowerCase().includes(query)
    );
    render(filtered);
  }

  searchInput.addEventListener('input', applyFilter);
  render(data.jobs);
}

init();
```

- [ ] **Step 4: Create `index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bay Area Biopharma Jobs</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>Bay Area Biopharma Jobs</h1>
  <p id="last-updated"></p>
  <input type="text" id="search" placeholder="Search by title, company, or location...">
  <table>
    <thead>
      <tr><th>Title</th><th>Company</th><th>Location</th></tr>
    </thead>
    <tbody id="jobs-body"></tbody>
  </table>
  <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 5: Test the frontend locally**

Run: `python -m http.server 8000`

Open http://localhost:8000/ in a browser. Expected:
- Page shows "Last updated: <date>" matching the sample `scraped_at`.
- Table shows the 3 sample jobs.
- Typing "research" in the search box filters to the 2 "Research Associate"
  rows.
- Typing "bighat" or "biohat" (a substring of nothing) shows zero rows;
  typing "BigHat" (case-insensitive) shows the BigHat row.
- Clicking a job title opens its URL in a new tab.

Stop the server with Ctrl+C when done.

- [ ] **Step 6: Commit**

```bash
git add index.html app.js style.css jobs.json
git commit -m "Add static frontend with search/filter"
```

---

## Task 8: GitHub Actions scraper workflow

**Files:**
- Create: `.github/workflows/scrape.yml`

- [ ] **Step 1: Create the workflow file**

Create `.github/workflows/scrape.yml`:

```yaml
name: Scrape Jobs

on:
  schedule:
    - cron: '0 13 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - run: pip install -r requirements.txt

      - run: python -m scraper.run
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Commit updated jobs.json
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add jobs.json
          git diff --staged --quiet || git commit -m "Update job listings"
          git push
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/scrape.yml
git commit -m "Add scheduled scraper workflow"
```

This workflow will only run successfully once the repo is on GitHub and the
`ANTHROPIC_API_KEY` secret is set (Task 9).

---

## Task 9: Deployment

**Files:** none (GitHub repo + Pages configuration)

- [ ] **Step 1: Create the GitHub repository and push**

```bash
gh repo create biopharma-job-board --public --source=. --remote=origin --push
```

Expected: a new public GitHub repo is created and this repo's commits are
pushed to it.

- [ ] **Step 2: Add the Anthropic API key as a repo secret**

```bash
gh secret set ANTHROPIC_API_KEY
```

This will prompt for the value — paste your Claude API key.

- [ ] **Step 3: Enable GitHub Pages**

```bash
gh api repos/{owner}/biopharma-job-board/pages -X POST -f "source[branch]=main" -f "source[path]=/"
```

Replace `{owner}` with your GitHub username (find it with `gh api user --jq .login`).

- [ ] **Step 4: Verify the live site**

Run: `gh api repos/{owner}/biopharma-job-board/pages --jq .html_url`

Open the returned URL in a browser. Expected: the job board loads, showing
the sample `jobs.json` data committed in Task 7.

- [ ] **Step 5: Trigger the scraper workflow manually**

```bash
gh workflow run scrape.yml
```

Wait a minute, then check the run status:

```bash
gh run list --workflow=scrape.yml --limit 1
```

Expected: the run completes successfully and `jobs.json` in the repo is
updated with real data from `companies.json`. Refresh the live site to see
the real listings.

---

## Self-review notes

- **Spec coverage:** companies.json (Task 2), scraper with Claude fallback
  (Tasks 3-6), static frontend with search (Task 7), GitHub Actions cron
  (Task 8), GitHub Pages deployment (Task 9), testing (unit tests in Tasks
  3-6, manual frontend check in Task 7) — all design sections are covered.
- **Out of scope items** (JS-rendered/Workday pages, accounts/alerts, resume
  matching, expanding past 25 companies) are intentionally not addressed by
  any task, per the design doc.
