# Job Posting Dates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `date_posted` field to every scraped job (sourced per-fetcher) and let users filter the job board by posting recency.

**Architecture:** Each of the three scraper fetchers (`greenhouse.py`, `lever.py`, `html_extract.py`) gains a `date_posted` field in the dicts it returns — Greenhouse passes through `updated_at`, Lever converts `createdAt` (epoch ms) to an ISO UTC string, and HTML/Claude-sourced jobs get `null`. The frontend (`index.html`, `style.css`, `app.js`) adds a "Posted" column and a recency `<select>` that combines with the existing text search via AND logic.

**Tech Stack:** Python 3 (requests, pytest, requests-mock), vanilla JS/HTML/CSS

**Spec:** `docs/superpowers/specs/2026-06-10-job-posting-dates-design.md`

---

### Task 1: Greenhouse fetcher — add `date_posted`

**Files:**
- Modify: `tests/fixtures/greenhouse_jobs.json`
- Modify: `tests/test_greenhouse.py`
- Modify: `scraper/greenhouse.py`

- [ ] **Step 1: Update the fixture to include `updated_at` per job**

Replace the full contents of `tests/fixtures/greenhouse_jobs.json` with:

```json
{
  "jobs": [
    {
      "id": 4699427005,
      "title": "Associate Director, Clinical Trial Management",
      "location": {"name": "San Francisco Bay Area"},
      "absolute_url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/4699427005",
      "updated_at": "2026-06-01T08:00:00-05:00"
    },
    {
      "id": 4684932005,
      "title": "Director, Procurement Strategic Contract Negotiator",
      "location": {"name": "San Francisco Bay Area"},
      "absolute_url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/4684932005",
      "updated_at": "2026-05-28T10:30:00-05:00"
    }
  ],
  "meta": {"total": 2}
}
```

- [ ] **Step 2: Update the test to assert `date_posted`**

Replace the full contents of `tests/test_greenhouse.py` with:

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
            "date_posted": "2026-06-01T08:00:00-05:00",
        },
        {
            "company": "Annexon Biosciences",
            "title": "Director, Procurement Strategic Contract Negotiator",
            "location": "San Francisco Bay Area",
            "url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/4684932005",
            "date_posted": "2026-05-28T10:30:00-05:00",
        },
    ]
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `python -m pytest tests/test_greenhouse.py -v`
Expected: FAIL — the actual job dicts returned by `fetch_greenhouse_jobs` won't contain a `date_posted` key, so the equality assertion fails.

- [ ] **Step 4: Implement the fetcher change**

Replace the full contents of `scraper/greenhouse.py` with:

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
            "date_posted": job["updated_at"],
        }
        for job in data.get("jobs", [])
    ]
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `python -m pytest tests/test_greenhouse.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/greenhouse_jobs.json tests/test_greenhouse.py scraper/greenhouse.py
git commit -m "feat: add date_posted to greenhouse fetcher"
```

---

### Task 2: Lever fetcher — add `date_posted`

**Files:**
- Modify: `tests/fixtures/lever_jobs.json`
- Modify: `tests/test_lever.py`
- Modify: `scraper/lever.py`

- [ ] **Step 1: Update the fixture to include `createdAt` per job**

Replace the full contents of `tests/fixtures/lever_jobs.json` with:

```json
[
  {
    "id": "a1b2c3d4-0000-0000-0000-000000000001",
    "text": "Senior Scientist, Protein Engineering",
    "categories": {"location": "Redwood City, CA"},
    "hostedUrl": "https://jobs.lever.co/boltbio/a1b2c3d4-0000-0000-0000-000000000001",
    "createdAt": 1748764800000
  },
  {
    "id": "a1b2c3d4-0000-0000-0000-000000000002",
    "text": "Research Associate, Antibody Discovery",
    "categories": {"location": "Redwood City, CA"},
    "hostedUrl": "https://jobs.lever.co/boltbio/a1b2c3d4-0000-0000-0000-000000000002",
    "createdAt": 1746000000000
  }
]
```

- [ ] **Step 2: Update the test to assert `date_posted`**

Replace the full contents of `tests/test_lever.py` with:

```python
import json
from datetime import datetime, timezone
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
            "date_posted": datetime.fromtimestamp(
                FIXTURE[0]["createdAt"] / 1000, tz=timezone.utc
            ).isoformat(),
        },
        {
            "company": "Bolt Biotherapeutics",
            "title": "Research Associate, Antibody Discovery",
            "location": "Redwood City, CA",
            "url": "https://jobs.lever.co/boltbio/a1b2c3d4-0000-0000-0000-000000000002",
            "date_posted": datetime.fromtimestamp(
                FIXTURE[1]["createdAt"] / 1000, tz=timezone.utc
            ).isoformat(),
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

- [ ] **Step 3: Run the test to verify it fails**

Run: `python -m pytest tests/test_lever.py -v`
Expected: FAIL — `test_fetch_lever_jobs` fails because the returned dicts don't contain `date_posted`.

- [ ] **Step 4: Implement the fetcher change**

Replace the full contents of `scraper/lever.py` with:

```python
from datetime import datetime, timezone

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
            "date_posted": datetime.fromtimestamp(
                job["createdAt"] / 1000, tz=timezone.utc
            ).isoformat(),
        }
        for job in data
    ]
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `python -m pytest tests/test_lever.py -v`
Expected: PASS (2 passed)

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/lever_jobs.json tests/test_lever.py scraper/lever.py
git commit -m "feat: add date_posted to lever fetcher"
```

---

### Task 3: HTML/Claude fetcher — add `date_posted: None`

**Files:**
- Modify: `tests/test_html_extract.py`
- Modify: `scraper/html_extract.py`

- [ ] **Step 1: Update the test to assert `date_posted: None`**

In `tests/test_html_extract.py`, replace the `test_fetch_html_jobs` function (lines 37-62) with:

```python
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
            "date_posted": None,
        },
        {
            "company": "BigHat Biosciences",
            "title": "Director/Senior Director, Antibody Discovery",
            "location": "San Mateo, CA",
            "url": "https://example.com/en/jobs/484931",
            "date_posted": None,
        },
    ]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_html_extract.py -v`
Expected: FAIL — `test_fetch_html_jobs` fails because the returned dicts don't contain `date_posted`. The other tests in this file (`test_clean_html_removes_script_tags`, `test_extract_json_array_handles_markdown_fences`) still pass.

- [ ] **Step 3: Implement the fetcher change**

In `scraper/html_extract.py`, replace the `return` statement of `fetch_html_jobs` (the final 8 lines, currently lines 55-62) with:

```python
    return [
        {
            "company": company_name,
            "title": job["title"],
            "location": job.get("location", ""),
            "url": job["url"],
            "date_posted": None,
        }
        for job in jobs
    ]
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest tests/test_html_extract.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Run the full test suite**

Run: `python -m pytest -v`
Expected: All 7 tests pass.

- [ ] **Step 6: Commit**

```bash
git add tests/test_html_extract.py scraper/html_extract.py
git commit -m "feat: add date_posted to html/claude fetcher"
```

---

### Task 4: Frontend — Posted column and recency filter

**Files:**
- Modify: `index.html`
- Modify: `style.css`
- Modify: `app.js`

- [ ] **Step 1: Update `index.html`**

Replace the full contents of `index.html` with:

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
  <div class="filters">
    <input type="text" id="search" placeholder="Search by title, company, or location...">
    <select id="recency">
      <option value="all">All time</option>
      <option value="24h">Last 24 hours</option>
      <option value="7d">Last 7 days</option>
      <option value="30d">Last 30 days</option>
    </select>
  </div>
  <table>
    <thead>
      <tr><th>Title</th><th>Company</th><th>Location</th><th>Posted</th></tr>
    </thead>
    <tbody id="jobs-body"></tbody>
  </table>
  <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Update `style.css`**

Replace the full contents of `style.css` with:

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

.filters {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

#search {
  flex: 1;
  padding: 0.5rem;
  font-size: 1rem;
  box-sizing: border-box;
}

#recency {
  padding: 0.5rem;
  font-size: 1rem;
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

- [ ] **Step 3: Update `app.js`**

Replace the full contents of `app.js` with:

```javascript
async function init() {
  const response = await fetch('jobs.json');
  const data = await response.json();

  const lastUpdated = document.getElementById('last-updated');
  lastUpdated.textContent = `Last updated: ${new Date(data.scraped_at).toLocaleString()}`;

  const tbody = document.getElementById('jobs-body');
  const searchInput = document.getElementById('search');
  const recencySelect = document.getElementById('recency');

  const RECENCY_WINDOWS_MS = {
    '24h': 24 * 60 * 60 * 1000,
    '7d': 7 * 24 * 60 * 60 * 1000,
    '30d': 30 * 24 * 60 * 60 * 1000,
  };

  function withinRecency(job, bucket) {
    if (bucket === 'all') return true;
    if (!job.date_posted) return false;
    const postedTime = new Date(job.date_posted).getTime();
    return Date.now() - postedTime <= RECENCY_WINDOWS_MS[bucket];
  }

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

      const postedCell = document.createElement('td');
      postedCell.textContent = job.date_posted
        ? new Date(job.date_posted).toLocaleDateString()
        : '—';

      row.append(titleCell, companyCell, locationCell, postedCell);
      tbody.appendChild(row);
    }
  }

  function applyFilter() {
    const query = searchInput.value.toLowerCase();
    const bucket = recencySelect.value;
    const filtered = data.jobs.filter(job =>
      (job.title.toLowerCase().includes(query) ||
      job.company.toLowerCase().includes(query) ||
      job.location.toLowerCase().includes(query)) &&
      withinRecency(job, bucket)
    );
    render(filtered);
  }

  searchInput.addEventListener('input', applyFilter);
  recencySelect.addEventListener('change', applyFilter);
  render(data.jobs);
}

init();
```

Note: `'—'` is the em dash character (—), used instead of a literal Unicode character in the source for editor/encoding safety.

- [ ] **Step 4: Commit**

```bash
git add index.html style.css app.js
git commit -m "feat: add Posted column and recency filter to job board"
```

---

### Task 5: Manual frontend verification

**Files:**
- Temporary (not committed): a local copy of `jobs.json` with crafted `date_posted` values

This task verifies the "Posted" column and recency filter render and behave correctly using realistic data, without permanently altering the production `jobs.json` (which is overwritten daily by the scraper workflow and currently has 378 real job entries with no `date_posted` field — it will gain that field automatically the next time the scraper runs with the updated fetchers from Tasks 1-3).

- [ ] **Step 1: Create a temporary test data file**

Create `jobs.test.json` (untracked — do not `git add` this file) with the following content. It has three jobs covering all three `date_posted` cases: one within the last 24 hours, one within the last 7 days but older than 24 hours, and one with `date_posted: null`.

```json
{
  "scraped_at": "2026-06-10T06:14:59.278929+00:00",
  "jobs": [
    {
      "company": "Annexon Biosciences",
      "title": "Research Associate, Protein Sciences",
      "location": "San Francisco Bay Area",
      "url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/0000000001",
      "date_posted": "2026-06-10T02:00:00+00:00"
    },
    {
      "company": "Caribou Biosciences",
      "title": "Director of Clinical Operations",
      "location": "Hybrid, Berkeley, California, United States, Remote",
      "url": "https://job-boards.greenhouse.io/cariboubiosciencesinc/jobs/0000000002",
      "date_posted": "2026-06-04T08:00:00+00:00"
    },
    {
      "company": "BigHat Biosciences",
      "title": "Scientist II, Cell Line Engineering",
      "location": "San Mateo, CA",
      "url": "https://example.com/en/jobs/527616",
      "date_posted": null
    }
  ]
}
```

- [ ] **Step 2: Serve the site locally**

Run (in the project root, in the background):

```bash
python -m http.server 8000
```

- [ ] **Step 3: Temporarily point the frontend at the test data**

In `app.js`, temporarily change `fetch('jobs.json')` to `fetch('jobs.test.json')`. Do not commit this change — it gets reverted in Step 6.

- [ ] **Step 4: Load the page in a browser and verify**

Navigate to `http://localhost:8000/`. Verify:
- The "Posted" column shows a date for "Research Associate, Protein Sciences" and "Director of Clinical Operations", and shows "—" for "Scientist II, Cell Line Engineering".
- Selecting "Last 24 hours" in the recency dropdown shows only "Research Associate, Protein Sciences".
- Selecting "Last 7 days" shows "Research Associate, Protein Sciences" and "Director of Clinical Operations", but not "Scientist II, Cell Line Engineering".
- Selecting "Last 30 days" shows the same two jobs as "Last 7 days".
- Selecting "All time" shows all three jobs.
- Typing into the search box still narrows results within the selected recency bucket (e.g., search "Caribou" with "Last 7 days" selected shows one row; search "Caribou" with "Last 24 hours" selected shows zero rows).

- [ ] **Step 5: Stop the local server**

Stop the `python -m http.server 8000` process started in Step 2.

- [ ] **Step 6: Revert the temporary changes**

Revert the `fetch('jobs.test.json')` change in `app.js` back to `fetch('jobs.json')`, and delete `jobs.test.json`:

```bash
git checkout app.js
rm jobs.test.json
```

Run `git status` to confirm the working tree is clean (no pending changes from this task).

---

## Summary

After all tasks: every newly scraped job will carry a `date_posted` field (ISO timestamp or `null` depending on source), and the job board UI will display a "Posted" column and let users filter by recency. The next scheduled run of `.github/workflows/scrape.yml` will regenerate `jobs.json` with `date_posted` populated for all 378+ current listings.
