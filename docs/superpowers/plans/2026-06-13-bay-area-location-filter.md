# Bay Area / Remote Location Filter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Filter the scraper's output so `jobs.json` only contains jobs located in the Bay Area or remote within the US/unspecified, dropping postings from other regions (e.g. Boston, Paris, "Remote (Japan)").

**Architecture:** A new pure function `is_bay_area_or_remote(location)` in `scraper/location_filter.py` classifies a location string. `scraper/run.py` applies it to the combined job list before writing `jobs.json`, logging how many jobs were dropped.

**Tech Stack:** Python, pytest (existing test suite, no new dependencies).

---

### Task 1: Location filter module

**Files:**
- Create: `scraper/location_filter.py`
- Test: `tests/test_location_filter.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_location_filter.py`:

```python
import pytest

from scraper.location_filter import is_bay_area_or_remote


@pytest.mark.parametrize(
    "location",
    [
        "South San Francisco",
        "Redwood City, CA",
        "San Francisco (UCSF)",
        "Emeryville, California; Remote, United States",
        "USA - Carlsbad, CA; USA - South San Francisco, CA",
        "Hybrid, Berkeley, California, United States, Remote",
        "Remote",
        "USA - Remote",
        "Remote (United States)",
        "Remote, United States",
    ],
)
def test_keeps_bay_area_or_us_remote_jobs(location):
    assert is_bay_area_or_remote(location) is True


@pytest.mark.parametrize(
    "location",
    [
        "Boston, Massachusetts, United States",
        "Northern California, United States",
        "Sacramento, California, United States",
        "Los Angeles, California, United States",
        "Various Locations",
        "Remote (Japan)",
        "Remote (UK)",
        "APAC - Remote",
        "",
    ],
)
def test_drops_jobs_outside_bay_area_and_non_us_remote(location):
    assert is_bay_area_or_remote(location) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_location_filter.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.location_filter'`

- [ ] **Step 3: Implement `scraper/location_filter.py`**

Create `scraper/location_filter.py`:

```python
BAY_AREA_KEYWORDS = [
    "bay area",
    "san francisco",
    "redwood city",
    "emeryville",
    "berkeley",
    "brisbane",
    "foster city",
    "menlo park",
    "palo alto",
    "mountain view",
    "sunnyvale",
    "santa clara",
    "san jose",
    "fremont",
    "hayward",
    "oakland",
    "alameda",
    "vacaville",
    "novato",
    "san rafael",
    "san mateo",
    "burlingame",
    "san carlos",
    "union city",
    "pleasanton",
    "walnut creek",
    "hercules",
    "milpitas",
    "daly city",
    "belmont",
    "half moon bay",
    "petaluma",
    "vallejo",
    "richmond, ca",
    "concord, ca",
]

NON_US_REMOTE_MARKERS = [
    "japan",
    "uk",
    "italy",
    "spain",
    "switzerland",
    "netherlands",
    "france",
    "germany",
    "apac",
    "ireland",
    "canada",
    "australia",
    "china",
    "mexico",
    "brazil",
    "india",
]


def is_bay_area_or_remote(location):
    location_lower = location.lower()

    if any(keyword in location_lower for keyword in BAY_AREA_KEYWORDS):
        return True

    if "remote" in location_lower:
        if not any(marker in location_lower for marker in NON_US_REMOTE_MARKERS):
            return True

    return False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_location_filter.py -v`
Expected: PASS (19 tests)

- [ ] **Step 5: Commit**

```bash
git add scraper/location_filter.py tests/test_location_filter.py
git commit -m "feat: add Bay Area/remote location filter"
```

---

### Task 2: Integrate filter into the scraper run

**Files:**
- Modify: `scraper/run.py`
- Test: `tests/test_run.py`

- [ ] **Step 1: Write the failing test**

Add this test to `tests/test_run.py` (after the existing `test_run_writes_jobs_and_skips_failures` test):

```python
def test_run_filters_out_jobs_outside_bay_area(tmp_path, monkeypatch):
    companies = [
        {
            "name": "GoodCo",
            "type": "greenhouse",
            "token": "goodco",
            "careers_url": "https://goodco.example/careers",
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
                "location": "South San Francisco, California, United States",
                "url": "https://goodco.example/jobs/1",
            },
            {
                "company": name,
                "title": "Sales Director",
                "location": "Boston, Massachusetts, United States",
                "url": "https://goodco.example/jobs/2",
            },
        ],
    )

    run_module.run(companies_path=str(companies_path), output_path=str(output_path))

    data = json.loads(output_path.read_text())
    assert [job["title"] for job in data["jobs"]] == ["Research Associate"]
```

- [ ] **Step 2: Run tests to verify the new test fails**

Run: `python -m pytest tests/test_run.py -v`
Expected: FAIL on `test_run_filters_out_jobs_outside_bay_area` — both jobs are written to `jobs.json`, so the assertion on titles fails (`['Research Associate', 'Sales Director'] != ['Research Associate']`).

- [ ] **Step 3: Apply the filter in `scraper/run.py`**

Add the import at the top of `scraper/run.py` (alongside the existing fetcher imports):

```python
from scraper.greenhouse import fetch_greenhouse_jobs
from scraper.lever import fetch_lever_jobs
from scraper.html_extract import fetch_html_jobs
from scraper.location_filter import is_bay_area_or_remote
```

Then replace this block in `scraper/run.py`:

```python
    output = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "jobs": all_jobs,
    }
    Path(output_path).write_text(json.dumps(output, indent=2))
    logger.info("Wrote %d total jobs to %s", len(all_jobs), output_path)
```

with:

```python
    filtered_jobs = [job for job in all_jobs if is_bay_area_or_remote(job["location"])]
    logger.info(
        "Filtered out %d jobs outside the Bay Area/remote-US",
        len(all_jobs) - len(filtered_jobs),
    )

    output = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "jobs": filtered_jobs,
    }
    Path(output_path).write_text(json.dumps(output, indent=2))
    logger.info("Wrote %d total jobs to %s", len(filtered_jobs), output_path)
```

- [ ] **Step 4: Run the full test suite to verify everything passes**

Run: `python -m pytest -q`
Expected: PASS (27 tests: 7 existing + 19 from `tests/test_location_filter.py` in Task 1 + 1 new test in `tests/test_run.py`)

- [ ] **Step 5: Commit**

```bash
git add scraper/run.py tests/test_run.py
git commit -m "feat: apply Bay Area/remote location filter to scraper output"
```

---

## Notes

- This change does not re-run the scraper against live APIs. The next
  scheduled scrape after this is merged will produce a filtered `jobs.json`.
- No frontend changes — filtering happens at scrape time, in
  `scraper/run.py`.
