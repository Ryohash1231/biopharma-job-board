# BioPharmGuy Directory Scraper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `scraper/scrape_biopharmguy.py`, a standalone CLI tool that scrapes the BioPharmGuy Northern California biotech company directory and writes a `candidates.json` file in the format expected by `scraper/discover_companies.py`.

**Architecture:** Two pieces in one file: `parse_companies(html)` (pure function, uses `BeautifulSoup` to extract `{"name", "website"}` from each directory row) and `main(...)` (CLI entry point that fetches the hardcoded directory URL and writes the parsed list to JSON).

**Tech Stack:** Python, `requests` and `beautifulsoup4` (both already dependencies — `bs4` is already used in `scraper/html_extract.py`), pytest (existing test suite, no new dependencies).

---

### Task 1: Parse company rows from directory HTML

**Files:**
- Create: `scraper/scrape_biopharmguy.py`
- Test: `tests/test_scrape_biopharmguy.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_scrape_biopharmguy.py`:

```python
from scraper.scrape_biopharmguy import parse_companies


NORMAL_ROW = """
<table>
<tr class="even">
<td class="company"><a href="/company.php/10X Genomics" class="company" target="_blank"><img src="/images/url.png" alt="Add'l Locations" height="9"></a><a href="https://www.10xgenomics.com/" style="text-decoration:none" target="_blank">10X Genomics </a></td>
<td class="location">CA - Pleasanton</td>
<td class="description">Genomics Platform</td>
</tr>
</table>
"""

ROW_WITH_DESCRIPTION_LINK = """
<table>
<tr class="odd">
<td class="company"><a href="/company.php/Selvita" class="company" target="_blank"><img src="/images/url.png" alt="Add'l Locations" height="9"></a><a href="https://selvita.com/" style="text-decoration:none" target="_blank">Selvita </a></td>
<td class="location">CA - South SF</td>
<td class="description">Selvita | Fully-integrated <a href="https://selvita.com/cro" target="_blank" rel="nofollow">CRO</a> providing support.</td>
</tr>
</table>
"""

SPONSOR_ROW = """
<table>
<tr class="sponsor">
<td class="company"><a href="https://www.mispro.com/space-services" style="text-decoration:none" target="_blank"><img class="database" src="/images/companies/mispro.png" alt="Mispro Biotech Services"> </a></td>
<td class="location">CA - South SF</td>
<td class="description">Mispro is a contract vivarium organization.</td>
</tr>
</table>
"""

ROW_WITHOUT_WEBSITE_LINK = """
<table>
<tr class="even">
<td class="company"><a href="/company.php/BadCo" class="company" target="_blank"><img src="/images/url.png" alt="Add'l Locations" height="9"></a></td>
<td class="location">CA - Somewhere</td>
<td class="description">No website link</td>
</tr>
</table>
"""


def test_parse_companies_extracts_name_and_website():
    result = parse_companies(NORMAL_ROW)

    assert result == [
        {"name": "10X Genomics", "website": "https://www.10xgenomics.com/"}
    ]


def test_parse_companies_ignores_links_in_description():
    result = parse_companies(ROW_WITH_DESCRIPTION_LINK)

    assert result == [
        {"name": "Selvita", "website": "https://selvita.com/"}
    ]


def test_parse_companies_skips_sponsor_rows():
    result = parse_companies(SPONSOR_ROW)

    assert result == []


def test_parse_companies_skips_rows_without_website_link():
    result = parse_companies(ROW_WITHOUT_WEBSITE_LINK)

    assert result == []


def test_parse_companies_handles_multiple_rows():
    html = NORMAL_ROW.replace("</table>", "") + ROW_WITH_DESCRIPTION_LINK.replace("<table>", "")

    result = parse_companies(html)

    assert result == [
        {"name": "10X Genomics", "website": "https://www.10xgenomics.com/"},
        {"name": "Selvita", "website": "https://selvita.com/"},
    ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_scrape_biopharmguy.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.scrape_biopharmguy'`

- [ ] **Step 3: Implement `parse_companies`**

Create `scraper/scrape_biopharmguy.py`:

```python
import logging

from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_companies(html):
    soup = BeautifulSoup(html, "html.parser")
    companies = []

    for row in soup.find_all("tr", class_=["odd", "even"]):
        company_cell = row.find("td", class_="company")
        if company_cell is None:
            logger.warning("Skipping row with no company cell")
            continue

        link = company_cell.find(
            "a", style=lambda value: value and "text-decoration:none" in value
        )
        if link is None:
            logger.warning("Skipping row with no company website link")
            continue

        companies.append({
            "name": link.get_text().strip(),
            "website": link["href"],
        })

    return companies
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_scrape_biopharmguy.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add scraper/scrape_biopharmguy.py tests/test_scrape_biopharmguy.py
git commit -m "feat: parse company rows from biopharmguy directory HTML"
```

---

### Task 2: CLI entry point

**Files:**
- Modify: `scraper/scrape_biopharmguy.py`
- Test: `tests/test_scrape_biopharmguy.py`

- [ ] **Step 1: Write the failing test**

Add these imports to the top of `tests/test_scrape_biopharmguy.py` (alongside the existing import):

```python
import json

import scraper.scrape_biopharmguy as scrape_module
from scraper.scrape_biopharmguy import main, parse_companies
```

Replace the existing single-line import (`from scraper.scrape_biopharmguy import parse_companies`) with the two lines above.

Then add this test at the end of `tests/test_scrape_biopharmguy.py`:

```python
class FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


def test_main_writes_candidates_json(tmp_path, monkeypatch):
    monkeypatch.setattr(
        scrape_module.requests,
        "get",
        lambda url, timeout: FakeResponse(NORMAL_ROW),
    )

    output_path = tmp_path / "candidates.json"

    main(output_path=str(output_path))

    data = json.loads(output_path.read_text())
    assert data == [
        {"name": "10X Genomics", "website": "https://www.10xgenomics.com/"}
    ]
```

- [ ] **Step 2: Run tests to verify the new test fails**

Run: `python -m pytest tests/test_scrape_biopharmguy.py -v`
Expected: FAIL — `ImportError: cannot import name 'main' from 'scraper.scrape_biopharmguy'` (and `AttributeError: module 'scraper.scrape_biopharmguy' has no attribute 'requests'` once `main` exists but before `requests` is imported)

- [ ] **Step 3: Implement `main` and CLI entry point**

Replace the import block at the top of `scraper/scrape_biopharmguy.py` (currently `import logging` followed by `from bs4 import BeautifulSoup`) with:

```python
import json
import logging
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DIRECTORY_URL = "https://biopharmguy.com/links/company-by-name-northern-california.php"
```

(This removes the now-duplicated `logging.basicConfig`/`logger` lines that
were already at the top of the file — keep only one copy, as shown above.)

Then add this code at the end of `scraper/scrape_biopharmguy.py`:

```python
def main(output_path="candidates.json"):
    response = requests.get(DIRECTORY_URL, timeout=10)
    response.raise_for_status()

    companies = parse_companies(response.text)

    Path(output_path).write_text(json.dumps(companies, indent=2))
    logger.info("Scraped %d companies from biopharmguy.com", len(companies))


if __name__ == "__main__":
    output_arg = sys.argv[1] if len(sys.argv) > 1 else "candidates.json"
    main(output_arg)
```

- [ ] **Step 4: Run the full test suite to verify everything passes**

Run: `python -m pytest -q`
Expected: PASS (46 tests: 40 existing + 6 from `tests/test_scrape_biopharmguy.py`)

- [ ] **Step 5: Commit**

```bash
git add scraper/scrape_biopharmguy.py tests/test_scrape_biopharmguy.py
git commit -m "feat: add CLI entry point for biopharmguy directory scraper"
```

---

## Notes

- Usage: `python -m scraper.scrape_biopharmguy [candidates.json]`. Defaults
  to writing `candidates.json` in the current directory.
- This script is not wired into `scraper/run.py` or the scheduled scrape
  workflow — it's a standalone tool the user runs manually to generate
  input for `scraper/discover_companies.py`.
- The user is responsible for running
  `python -m scraper.discover_companies candidates.json` next and reviewing
  `discovered_companies.json`.
